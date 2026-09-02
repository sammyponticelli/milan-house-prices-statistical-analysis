# Milano Real Estate — Analisi Statistica

**Quali fattori influenzano il prezzo delle case a Milano, e cosa può dirci l'analisi statistica sul mercato immobiliare?**

L'analisi lavora su ~18k annunci di vendita raccolti da immobiliare.it e percorre l'intero strumentario statistico — dalla statistica descrittiva alla regressione lineare multipla — per arrivare a una **mappa del prezzo medio al metro quadro per zona**.

Il resoconto dei risultati sarà in **[REPORT.md](REPORT.md)**. Questo file documenta i dati, il metodo e il piano di lavoro.

> Il README è scritto in italiano durante lo sviluppo; verrà tradotto in inglese a progetto concluso.

---

## Dataset

`immobiliare_milano_vendita.csv` — **18.017 righe × 31 colonne**, annunci di vendita residenziale a Milano.

### Variabili usate nell'analisi

| Variabile | Tipo | Descrizione |
|---|---|---|
| `price` | float | Prezzo richiesto in € (50 mancanti) |
| `surface_mq` | float | Superficie in m² (29 mancanti) |
| `price_per_mq` | float | `price / surface_mq`, già calcolato nel file (79 mancanti) |
| `rooms` | stringa | Numero di locali — `1`…`5`, `5+`, più intervalli tipo `2 - 4` per i progetti multi-unità |
| `bedrooms` | float | Numero di camere da letto (2.014 mancanti) |
| `bathrooms` | stringa | `1`, `2`, `3`, `3+` (1.100 mancanti) |
| `floor` | stringa | Testo libero — `3`, `3 piano`, `piano terra`, `piano rialzato`, … (233 valori distinti) |
| `elevator` | float | **Solo `1.0` oppure mancante** — non esiste alcuno `0` esplicito |
| `condition` | stringa | `Nuovo / In costruzione`, `Ottimo / Ristrutturato`, `Buono / Abitabile`, `Da ristrutturare` |
| `heating` | stringa | `Centralizzato`, `Autonomo`, `Assente` |
| `is_new` | int | Flag nuova costruzione (419 annunci) |
| `luxury` | int | Flag segmento lusso (3.591 annunci) |
| `typology` | stringa | `Bilocale`, `Trilocale`, `Appartamento`, `Attico`, `Loft`, … |
| `microzone` | stringa | Zona fine, **144 distinte** (es. `Dergano`, `Maggiolina`) |
| `macrozone` | stringa | Zona aggregata, **32 distinte** (es. `Affori, Bovisa`) — variabile di raggruppamento delle fasi 4-5 |
| `lat`, `lon`, `has_geo` | float / int | Coordinate; 16.727 annunci sono geolocalizzati — è la chiave di aggancio della mappa |

### Variabili non usate nell'analisi statistica

| Variabile | Descrizione |
|---|---|
| `id`, `unit` | Identificativo dell'annuncio e indice della sotto-unità (vedi sotto) |
| `nil_id`, `nil` | NIL di appartenenza già presente nella sorgente — la fase 10 ricalcola comunque l'assegnazione per point-in-polygon |
| `url`, `title`, `address` | Testo libero / identificativi |
| `city`, `region` | Costanti (`Milano` / `Lombardia`) |
| `category` | `Residenziale` (16.469), `Nuove costruzioni` (137), `Palazzi - Edifici` (135) — usata come **filtro**, non come variabile |
| `agency` | Agenzia venditrice (569 mancanti) — possibile estensione, fuori dal modello principale |
| `is_outlier`, `price_is_range` | Flag di qualità già presenti nella sorgente — usati come **filtri** |

---

## Pulizia dei dati

**Fase completata.** Cinque decisioni, applicate prima di calcolare qualunque statistica. Implementate in `milano_analysis.py` come funzioni separate — ogni passaggio stampa un prima/dopo, così la cascata dei filtri resta ispezionabile e non solo dichiarata.

**1. Eliminare le sotto-unità.** Gli annunci multi-unità (progetti di nuova costruzione) compaiono come una riga padre `unit = 0` più una riga per appartamento `unit = 1, 2, 3…`, **tutte con lo stesso `price` ripetuto** (fino a 36 sotto-unità per un unico prezzo). Il filtro `unit == 0` rimuove **1.276 righe**: 18.017 → **16.741**. Le righe delle sotto-unità non hanno `category`, quindi il filtro successivo le rimuoverebbe comunque — ma il filtro esplicito su `unit` tiene l'intenzione visibile nel codice invece di affidarla a un effetto collaterale.

**2. Applicare i flag di qualità della sorgente.** Tre filtri in cascata, ed è la cascata il dato interessante:

| Filtro | Righe rimaste | Rimosse |
|---|---|---|
| dopo `unit == 0` | 16.741 | — |
| `category == 'Residenziale'` | 16.469 | 272 (`Nuove costruzioni` 137, `Palazzi - Edifici` 135) |
| `is_outlier == 0` | 16.346 | 123 |
| `price_is_range == 0` | 16.346 | **0** |

Sul file grezzo i flag marcano 1.567 outlier e 1.321 prezzi-intervallo, ma **la quasi totalità sta nelle righe già eliminate**: gli annunci con prezzo espresso come intervallo sono per costruzione i progetti multi-unità, e dopo i primi due filtri non ne resta nemmeno uno. Il filtro `price_is_range` a valle non scarta nulla — resta nel codice come verifica esplicita, non come passaggio attivo. È un caso in cui il risultato atteso (≈1.300 righe da scartare) e il risultato reale (zero) divergono, e la spiegazione della divergenza vale più del numero.

**3. Scartare le righe senza prezzo o superficie.** `price`, `surface_mq`, `price_per_mq` sono le tre variabili da cui dipende tutto il resto. Nel file grezzo mancano rispettivamente in 50, 29 e 79 righe; dopo i filtri di qualità i mancanti sono **0, 0 e 0** — anche qui i buchi erano concentrati nelle righe già rimosse. Il passaggio si è quindi ridotto a un controllo di conferma.

**4. `elevator` — il mancante significa "no".** Nel file grezzo la colonna assume i valori `1.0` (13.572) e `NaN` (4.445), senza alcuno zero. Non è una colonna con dei buchi: è una codifica a sola-presenza, il campo viene scritto solo quando l'annuncio dichiara l'ascensore. Viene quindi ricodificata in una dummy 0/1 pulita — sul dataset filtrato: **12.367 con ascensore, 3.979 senza**.

L'alternativa — trattare i `NaN` come dato mancante vero — comporterebbe l'esclusione automatica di **4.445 annunci, il 27% del dataset**, dalla regressione della fase 8. Ed è un'esclusione non casuale: gli annunci col campo vuoto sono sistematicamente immobili più vecchi, piccoli e periferici, cioè proprio il segmento che serve per stimare l'effetto dell'ascensore. Si perderebbero i dati *e* si introdurrebbe una distorsione, invece di evitarla.

Il rischio residuo della codifica scelta è che qualche immobile abbia davvero l'ascensore senza che il campo sia compilato. Quei casi finiscono etichettati come "senza" e **attenuano** β₅ verso lo zero: la stima dell'effetto risulta più piccola del vero, mai più grande. È un errore conservativo, e la fase 8 stima β₅ = 0,0789 sapendo che è semmai una sottostima. Una verifica empirica dell'assunzione non è però possibile — il perché sta nella fase 8, ed è a sua volta una conseguenza della codifica a sola-presenza.

**5. Parsare le colonne testuali sporche.** Tre colonne da stringa a numerico:

- `rooms` — `5+` → 5 (609 righe), gli intervalli tipo `2 - 4` vengono scartati per regex, ma sul dataset filtrato **non ne resta nessuno**: comparivano solo sulle righe multi-unità, già rimosse al passaggio 1. Nessuna riga persa qui.
- `bathrooms` — `3+` → 3 (313 righe).
- `floor` — normalizzato a minuscolo, poi `piano terra` → 0 (2.035 righe) e `piano rialzato` → 0,5 (1.267 righe); per il resto si estrae il primo numero, così `3 piano` → 3.

**Risultato: 16.346 annunci puliti** (90,7% del file grezzo), di cui **16.333 geolocalizzati**. Tutte e 32 le macrozone sopravvivono con almeno 115 annunci ciascuna — abbastanza per i confronti fra gruppi delle fasi 4-5 senza dover accorpare categorie. Zero duplicati.

### Mancanti residui sul dataset pulito

Le tre variabili portanti sono complete; ciò che resta scoperto sta sulle variabili di contorno, e va gestito in fase di modellazione anziché a monte:

| Variabile | Mancanti | Quota | Nota |
|---|---|---|---|
| `bathrooms` | 844 | 5,2% | rilevante per la fase 8 |
| `condition` | 587 | 3,6% | idem |
| `floor` | 544 | 3,3% | testo non riconducibile a un numero |
| `bedrooms` | 444 | 2,7% | fuori dal modello principale |
| `rooms` | 106 | 0,6% | |
| `lat` / `lon` / `nil` | 13 | 0,1% | escluse dalla mappa della fase 10 |
| `microzone` | 57 | 0,3% | `macrozone` ne manca solo 12 |

La regressione della fase 8 usa `rooms`, `bathrooms`, `condition` e `floor` insieme, e a listwise deletion la perdita cumulata è risultata di **1.707 righe, il 10,4%**: il modello completo gira su 14.639 annunci. I mancanti si sovrappongono solo in parte, quindi il costo totale è inferiore alla somma delle singole quote ma superiore alla più grande di esse.

**Un'anomalia da tenere d'occhio:** `floor` contiene un valore 41 (una riga) — a Milano è implausibile e va ispezionato prima della fase 7, dove entrano i residui. Gli altri estremi (19, 21) sono compatibili con le torri di Porta Nuova / CityLife.

---

## Struttura dell'analisi

### Phase 1 — Descriptive Statistics

**Fase completata.** Media, mediana, moda, varianza, deviazione standard, minimo, massimo, quartili, IQR, range, coefficiente di variazione e asimmetria, calcolati sulle tre variabili centrali: `price`, `surface_mq`, `price_per_mq` e raccolti in un'unica tabella (`descriptive_statistics`). A corredo, un **box plot** per ciascuna delle tre variabili (`plot_boxplots`), che rende visibile la stessa asimmetria che i numeri dichiarano: baffo superiore lunghissimo e una nuvola fitta di punti oltre il terzo quartile.

Il punto della fase è il confronto **fra** le variabili, non i numeri in sé:

| | media | mediana | CV | asimmetria |
|---|---|---|---|---|
| `price` | € 570.105 | € 379.000 | **1,18** | 5,68 |
| `surface_mq` | 95 m² | 80 m² | 0,67 | 3,42 |
| `price_per_mq` | € 5.622 | € 5.073 | **0,47** | 1,83 |

Due cose da leggerci dentro. Primo, media ≫ mediana ovunque: le distribuzioni sono asimmetriche a destra e **la media non è un buon riassunto dell'annuncio milanese tipico** — una manciata di immobili sopra i 10 M€ la trascina in alto della metà. Secondo, il coefficiente di variazione scende da 1,18 a 0,47 una volta normalizzato il prezzo per la superficie: gran parte della variabilità grezza del prezzo è semplicemente variabilità di dimensione. È il primo vero risultato del progetto, e giustifica l'uso di `price_per_mq` come variabile di confronto dalla fase 4 in avanti.

### Phase 2 — Probability & Distributions

**Fase completata.** Cinque passaggi, tutti sulle stesse tre variabili centrali:

- **Istogrammi** (`plot_hist`), con media e mediana marcate da due linee verticali sul grafico perché l'asimmetria si veda invece di essere dedotta dalla tabella della fase 1.
- **Q-Q plot** contro la normale (`plot_qq`, via `scipy.stats.probplot`). La coda destra si stacca dalla diagonale in modo netto: è la stessa asimmetria di prima, letta sui quantili.
- **Percentili** p1, p5, p10, p25, p50, p75, p90, p95, p99 (`percentile_statistics`) — su una distribuzione come questa una tabella di percentili dice molto più di una media.
- **Indici di forma** (`distribution_shape`): curtosi accanto all'asimmetria, in un'unica tabella.
- **Trasformazione logaritmica** di `price` (`log_transform`), con le due scale mostrate affiancate — istogramma e curva normale sovrapposta a sinistra sul prezzo grezzo, a destra su `log(price)` (`plot_log_comparison`). La curva normale sovrapposta all'istogramma delle tre variabili in scala originale sta in `plot_normal_distribution`.

**Percentili**

| | p1 | p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|---|---|
| `price` (€) | 85.950 | 190.800 | 260.000 | 379.000 | 600.000 | 1.090.000 | 3.511.000 |
| `surface_mq` (m²) | 25 | 45 | 56 | 80 | 110 | 160 | 360 |
| `price_per_mq` (€/m²) | 1.576 | 3.045 | 3.941 | 5.073 | 6.695 | 8.762 | 15.399 |

Il salto p90 → p99 sul prezzo è di quasi 2,5 M€: il 10% più caro del mercato è un mondo a parte, e da solo spiega perché la media della fase 1 stia a € 570.105 contro una mediana di € 379.000. Sul prezzo al m² la stessa distanza si comprime — da € 8.762 a € 15.399, meno del doppio — perché normalizzare per la superficie toglie di mezzo la dimensione e lascia solo il premio di posizione e di qualità.

**Forma della distribuzione**

| | asimmetria | curtosi (in eccesso) |
|---|---|---|
| `price` | 5,68 | **54,98** |
| `surface_mq` | 3,42 | 19,79 |
| `price_per_mq` | 1,83 | 5,88 |

La curtosi aggiunge l'informazione che l'asimmetria da sola non dà: 54,98 contro lo 0 della normale significa code enormemente più pesanti: gli eventi estremi non sono rari come una normale con la stessa media e la stessa deviazione standard prevederebbe. La curva normale sovrapposta all'istogramma lo rende evidente: la gaussiana adattata su media e σ del prezzo è troppo larga al centro e troppo sottile in coda — non sbaglia di poco, sbaglia la forma.

**Trasformazione logaritmica**

`log(price)` porta l'asimmetria da **5,68 a 0,66** e la curtosi da **54,98 a 1,34**. Non è una normale — non lo è mai nessun dato reale — ma è abbastanza vicino alla simmetria da rendere difendibile l'apparato parametrico delle fasi 4-8, ed è la giustificazione empirica della specificazione log-log della fase 7. Sul prezzo al m² il logaritmo fa ancora meglio (asimmetria −0,07).

Una nota di metodo: con n = 16.346 i test formali di normalità (Shapiro-Wilk, D'Agostino) rifiutano l'ipotesi nulla su qualunque dataset, perché la potenza nel rilevare una deviazione irrilevante è di fatto pari a 1. La fase si appoggia quindi ai **Q-Q plot e agli indici di forma**, spiegando perché il test non viene usato.

### Phase 3 — Sampling & Confidence Intervals

**Fase completata.** Questa fase tratta i 16.346 annunci puliti come **popolazione** — i suoi parametri sono noti — e ne estrae campioni, così che stima e verità siano effettivamente confrontabili. Tutto gira su `price_per_mq`.

- **Parametri di popolazione** (`population_parameters`): μ = **€ 5.621,55**/m², σ = **€ 2.644,29**/m². σ è calcolata con `ddof=0` — è una popolazione, non un campione, e il denominatore giusto è N.
- **Distribuzione della media campionaria** (`draw_sample`): 1.000 campioni senza reinserimento per ciascuna numerosità n = 30, 100, 500, con l'istogramma delle 1.000 medie per ogni n.
- **Errore standard empirico contro teorico**, nella stessa funzione: deviazione standard delle 1.000 medie a confronto con σ/√n.
- **Intervalli di confidenza al 95%** con la distribuzione *t* e **verifica della copertura** (`confidence_intervals`): per ciascun n si costruiscono 1.000 intervalli — ognuno dalla sua media e dalla sua deviazione standard campionaria, come farebbe chi ha in mano un solo campione — e si conta quanti contengono davvero μ.

**Teorema del limite centrale in pratica**

| n | SE empirico | σ/√n teorico |
|---|---|---|
| 30 | € 482,82 | € 482,78 |
| 100 | € 262,73 | € 264,43 |
| 500 | € 120,82 | € 118,26 |

Le due colonne coincidono a meno di pochi euro — a n = 30 le prime tre cifre sono le stesse — e la dispersione si riduce passando da n = 100 a n = 500 del fattore √5 previsto, su una popolazione con asimmetria 1,83 dove la singola osservazione non è affatto normale. L'istogramma delle medie campionarie è invece simmetrico e campanulare già a n = 30: è il CLT che si vede, non che si cita.

Un termine di confronto più esatto esisterebbe: i campioni sono estratti **senza reinserimento** da una popolazione finita, quindi la formula corretta è σ/√n moltiplicata per il fattore di popolazione finita √((N−n)/(N−1)), che a n = 500 porta il valore teorico da € 118,26 a € 116,40. La correzione è trascurabile perché n resta piccolo rispetto a N = 16.346, e il confronto è lasciato sulla formula standard perché è quella di cui la fase discute.

**Copertura degli intervalli**

| n | copertura osservata |
|---|---|
| 30 | **94,2%** |
| 100 | **93,8%** |
| 500 | **94,5%** |

Tutte e tre stanno sotto il 95% nominale, ma la lettura corretta di questa tabella richiede di sapere quanto vale il suo margine d'errore. Ogni copertura è essa stessa una stima, ricavata da 1.000 ripetizioni: il suo errore Monte Carlo vale circa **±0,7 punti**. Le tre cifre sono quindi compatibili sia fra loro sia con il 95%, e **da questa singola esecuzione non si può concludere granché** — men che meno che n = 100 copra peggio di n = 30, che è quello che la tabella sembra dire.

L'andamento vero si vede solo ripetendo l'intero esperimento. Su **sei serie indipendenti** da 1.000 intervalli ciascuna la copertura media risulta:

| n | media di 6 serie | intervallo osservato |
|---|---|---|
| 30 | **93,53%** | 93,0 – 93,9 |
| 100 | 94,50% | 93,8 – 95,9 |
| 500 | 95,17% | 94,5 – 96,2 |

Adesso il quadro è leggibile. A n = 30 tutte e sei le serie cadono fra 93,0 e 93,9, senza mai avvicinarsi al 95%: la sotto-copertura è sistematica, e la deviazione standard fra serie (0,35 punti) è troppo piccola perché si tratti di rumore. A n = 500 la media risale a 95,17%, cioè al valore nominale. Serve un ordine di grandezza in più di ripetizioni per vedere emergere dal rumore quello che una sola tabella non può mostrare. La spiegazione è quella attesa — l'intervallo *t* assume una popolazione normale, qui l'asimmetria è 1,83 e a n = 30 il CLT non ha ancora finito il suo lavoro, così l'intervallo mantiene meno di quanto promette — ma è una spiegazione che questa singola tabella **non basta a dimostrare**.

È il risultato metodologico della fase, e vale più di una copertura ordinata: il livello di confidenza è una proprietà **della procedura sotto le sue assunzioni**, e misurarla richiede a sua volta abbastanza dati per distinguere il segnale dal rumore. Portare le ripetizioni da 1.000 a 10.000 ridurrebbe il margine a ±0,2 punti e renderebbe la tabella leggibile per quello che sembra dire.

**Nota sulla riproducibilità:** `draw_sample` e `confidence_intervals` costruiscono ciascuna un generatore `np.random.default_rng(42)` e lo passano a ogni `.sample(...)`. Due esecuzioni consecutive danno output identico riga per riga, verificato. Il generatore va creato **una volta fuori dal ciclo** e lasciato avanzare: passare `random_state=42` direttamente a `.sample()` produrrebbe 1.000 copie dello stesso campione, non 1.000 campioni riproducibili.

### Phase 4 — Hypothesis Testing

**Fase completata.** Confronti formali fra due campioni su `price_per_mq`, tutti bilaterali con α = 0,05.

L'apparato del test sta in **una sola funzione riusabile**, `two_sample_test(group_1, group_2)`, che restituisce test di Levene, t-test di Welch, gradi di libertà, intervallo di confidenza al 95% per la differenza fra le medie e d di Cohen. `hypothesis_testing` si limita a estrarre i gruppi e a chiamarla quattro volte: la logica statistica è scritta e verificata una volta sola, i confronti sono dati. I gradi di libertà di Welch–Satterthwaite e l'intervallo di confidenza sono calcolati esplicitamente dalla formula, non letti da un output già pronto — è la fase in cui costruire il test a mano è il punto.

**Test 1 — due zone.**

> **H₀**: μ(zona A) = μ(zona B) — il prezzo medio al m² è uguale nelle due zone
> **H₁**: μ(zona A) ≠ μ(zona B) — bilaterale

Due coppie scelte apposta per contrasto: una lontanissima, dove l'esito è scontato e la quantità interessante è la dimensione dell'effetto; e una ravvicinata — `Ripamonti, Vigentino` contro `Porta Vittoria, Lodi`, centroidi a 2,4 km, n quasi identici — dove il test fa un lavoro vero.

| | `Centro` vs `Bisceglie, Baggio, Olmi` | `Ripamonti, Vigentino` vs `Porta Vittoria, Lodi` |
|---|---|---|
| n | 389 vs 426 | 511 vs 518 |
| media €/m² | 11.812 vs 3.301 | 4.953 vs 5.164 |
| differenza | **+8.511** | **−211** |
| t (Welch) | 38,90 | −2,26 |
| gradi di libertà | 428,8 | 1.023,4 |
| p | 9,6 × 10⁻¹⁴³ | **0,024** |
| IC 95% della differenza | [8.081; 8.941] | **[−393; −28]** |
| d di Cohen | **2,84** | **−0,14** |
| Levene (p) | 5,7 × 10⁻⁶⁴ | 0,324 |

Le due colonne dicono la stessa cosa — "rifiuta H₀" — e non significano niente di simile.

A sinistra d = 2,84: le due distribuzioni sono separate di quasi tre deviazioni standard, il p-value è un numero senza contenuto informativo e la quantità che conta è l'intervallo di confidenza, che colloca il divario fra € 8.081 e € 8.941 al m².

A destra sta il risultato didattico della fase. p = 0,024 rifiuta H₀ ad α = 0,05, ma **d = −0,14 è un effetto trascurabile** per le convenzioni di Cohen (piccolo = 0,2), e soprattutto l'intervallo di confidenza — [−393; −28] — ha l'estremo superiore a 28 €/m² dallo zero. Su un appartamento di 80 m² il vero divario fra le due zone potrebbe essere di € 31.000 come di € 2.200: il test ha stabilito che le due zone non sono identiche, e null'altro. È esattamente il motivo per cui la dimensione dell'effetto e l'intervallo di confidenza stanno accanto a ogni p-value, e non è un avvertimento astratto — con n ≈ 500 per gruppo, una differenza del 4% supera la soglia di significatività.

**Test 2 — una caratteristica dell'immobile.** Lo stesso apparato applicato a `elevator` e a `condition`, per mostrare che la verifica d'ipotesi non riguarda solo la geografia.

| | `elevator` sì vs no | `Da ristrutturare` vs `Ottimo / Ristrutturato` |
|---|---|---|
| n | 12.367 vs 3.979 | 1.560 vs 7.004 |
| media €/m² | 5.894 vs 4.773 | 5.160 vs 6.145 |
| differenza | **+1.121** | **−984** |
| t (Welch) | 26,13 | −14,28 |
| gradi di libertà | 8.072,5 | 2.554,0 |
| p | 1,6 × 10⁻¹⁴⁴ | 1,5 × 10⁻⁴⁴ |
| IC 95% della differenza | [1.037; 1.205] | [−1.120; −849] |
| d di Cohen | 0,43 | −0,37 |
| Levene (p) | 4,8 × 10⁻¹⁹ | 1,1 × 10⁻⁴ |

Entrambi gli effetti sono nettamente significativi e di dimensione media — d = 0,43 e d = −0,37, un ordine di grandezza sopra quello della coppia di zone ravvicinate. Sono però **differenze grezze, senza alcun controllo**: l'ascensore è più frequente negli edifici recenti e centrali, e gli immobili da ristrutturare sono sistematicamente più grandi e più vecchi. Quanto di questi 1.121 €/m² appartenga davvero all'ascensore, e non alla zona o al tipo di edificio in cui l'ascensore si trova, è una domanda che il t-test non può porsi: serve la regressione multipla della fase 8, dove le stesse variabili rientrano controllate per zona e superficie. Il confronto fra il coefficiente della fase 8 e la differenza grezza qui sopra è uno dei risultati previsti della fase 9.

**Su Levene e Welch.** Il test di Levene rifiuta l'omogeneità delle varianze in **tre casi su quattro** — clamorosamente per `Centro` contro periferia (σ = 4.206 contro 1.009), dove le due zone non hanno in comune nemmeno l'ordine di grandezza della dispersione. Solo per la coppia ravvicinata non rifiuta (p = 0,324). Si usa comunque **Welch dappertutto**: quando le varianze sono davvero omogenee Welch coincide in pratica con Student — e infatti lì i gradi di libertà scendono a 1.023,4 contro i 1.027 di Student, una differenza irrilevante — mentre quando non lo sono, Student sbaglia. Un test che non costa nulla nel caso favorevole e salva nel caso sfavorevole non ha bisogno di essere scelto caso per caso. Si noti anche il crollo dei gradi di libertà nel primo confronto: 428,8 contro gli 813 di Student, ed è Welch che sconta la varianza sproporzionata di `Centro`.

La discussione copre l'**errore di tipo I** (rifiutare una H₀ vera — il 5% che accettiamo fissando α), l'**errore di tipo II** e il motivo per cui un n grande rende "significative" differenze minuscole e prive di senso — cosa che in questa fase non è un'ipotesi ma un risultato misurato, la colonna di destra della prima tabella.

### Phase 5 — ANOVA

**Fase completata.** L'estensione naturale della fase 4 a tutte e **32 le macrozone** insieme, su **16.334 annunci** (i 12 senza `macrozone` escludono sé stessi). Cinque funzioni orchestrate da `anova_phase`: `anova_analysis`, `welch_anova`, `residual_diagnostics`, `tukey_posthoc`, `plot_macrozone_boxplots`.

> **H₀**: μ₁ = μ₂ = … = μ₃₂ — il prezzo medio al m² è uguale in ogni zona di Milano
> **H₁**: almeno una zona differisce

**ANOVA a una via** (`anova_analysis`)

| | |
|---|---|
| F | **658,07** |
| gradi di libertà | 31; 16.302 |
| p | < 10⁻³⁰⁰ (restituito come 0.0) |
| η² | **0,556** |

H₀ è respinta senza margine di discussione, ma anche qui il p-value è la parte meno interessante: con oltre 16.000 osservazioni e un rapporto di 3,6 volte fra la zona più cara e la più economica, nessun altro esito era concepibile. La quantità che porta informazione è **η² = 0,556**: la sola appartenenza a una macrozona spiega il **55,6% della varianza del prezzo al m²**. Metà abbondante di ciò che distingue un annuncio da un altro, una volta tolta di mezzo la superficie, è geografia — ed è il numero che giustifica sia le dummy di zona della fase 8 sia l'intero deliverable della fase 10. η² è calcolato a mano dalla devianza fra i gruppi su quella totale, non ripreso da un output.

**Verifica delle assunzioni** (`welch_anova`, `residual_diagnostics`)

Levene: **statistica 89,40, p ≈ 0** — l'omogeneità delle varianze è violata in modo grossolano, come già lasciavano prevedere le deviazioni standard per zona (da € 826 a Forlanini a € 4.206 in Centro, un fattore 5). Da qui l'**ANOVA di Welch**, che non la assume: **F = 451,70** con gradi di libertà (31; 4.249,0) e p ≈ 0. Le due F non sono confrontabili fra loro come numeri — Welch penalizza pesantemente i gradi di libertà del denominatore, da 16.302 a 4.249 — ma la conclusione non si muove di un millimetro. È il caso in cui si dichiara che l'assunzione è violata **e** che il risultato regge lo stesso, invece di scegliere fra le due cose.

`charts/anova_residuals.png` mostra il perché in forma grafica. I valori stimati sono 32 soli — le medie di gruppo — quindi i residui si dispongono in 32 strisce verticali, e **le strisce si allargano da sinistra a destra**: attorno a € 4.000/m² i residui stanno entro ±5.000, attorno a € 12.000/m² sfiorano ±15.000. Le zone care non sono solo più care, sono internamente **più disomogenee**. Il Q-Q plot dei residui conferma la coda destra pesante già nota dalla fase 2: la normalità dei residui è anch'essa violata, e con n = 16.334 il teorema del limite centrale la rende una violazione di scarsa conseguenza per il test F, a differenza dell'eteroschedasticità.

**Post-hoc: Tukey HSD** (`tukey_posthoc`)

Su tutte le **496 coppie**, **426 risultano significative** (86%) e 70 no. La correzione è obbligatoria: 496 t-test indipendenti ad α = 0,05 produrrebbero per costruzione ~25 falsi positivi, cioè più di un terzo delle 70 coppie che qui restano non significative.

L'effetto della correzione si vede meglio su un caso già noto — **la coppia ravvicinata della fase 4**:

| | fase 4 (Welch, non corretto) | fase 5 (Tukey, corretto) |
|---|---|---|
| `Ripamonti, Vigentino` vs `Porta Vittoria, Lodi` | p = **0,024** → rifiuto | p-adj = **0,992** → non rifiuto |

Stessa differenza di 211 €/m², stessi dati, conclusione opposta. Nella fase 4 quel confronto era *l'unico* posto in cui si guardava; qui è uno dei 496, e il livello di confidenza è ricalibrato di conseguenza — l'intervallo di Tukey si allarga a [−626; +205] e include lo zero. Non è che uno dei due test sbagli: rispondono a due domande diverse, e la differenza fra le due è precisamente il problema dei confronti multipli.

Le coppie con lo scarto più grande sono tutte confronti fra `Centro` (o `Bisceglie, Baggio, Olmi`) e il resto della città — la massima è **`Bisceglie, Baggio, Olmi` contro `Centro`, +8.511 €/m²**, la stessa della fase 4. All'estremo opposto, la più piccola differenza che sopravvive alla correzione vale **360 €/m²** (`Famagosta, Barona` contro `Uptown, Cascina Merlata, Viale Certosa`, p-adj = 0,027): sotto quella soglia, con queste numerosità, Tukey non distingue più.

**Box plot per macrozona** (`plot_macrozone_boxplots`) — `charts/macrozone_boxplots.png`, le 32 zone ordinate per mediana crescente. È la controparte visiva del test e mostra tre cose che l'F non dice.

La salita è **continua**: dalla mediana di € 3.216 di `Bisceglie, Baggio, Olmi` a € 11.481 del `Centro` non c'è nessun salto, nessuna soglia che separi "centro" da "periferia". Milano, sul prezzo al m², è un gradiente e non due mercati.

La prima dozzina di zone forma però un **plateau**: da `Bisceglie` a `Udine, Lambrate` le mediane stanno tutte fra € 3.200 e € 4.500 — dodici zone in 1.300 € — mentre le ultime quattro coprono da sole quasi 2.000 €. È il motivo per cui le 70 coppie non significative di Tukey si concentrano quasi tutte in fondo alla classifica: là le zone sono davvero vicine.

E l'**ampiezza delle scatole cresce con la mediana**: l'IQR di `Bisceglie` sta dentro il migliaio di euro, quello del `Centro` supera i cinquemila. È la stessa eteroschedasticità del grafico dei residui, vista da un'altra angolazione — comprare in centro non significa solo pagare di più, significa entrare in un mercato molto meno prevedibile.

### Phase 6 — Correlation

**Fase completata.** Relazioni bivariate con `price`, ciascuna misurata **due volte**. Quattro funzioni sotto `correlation_phase`: `prepare_correlation_data` (codifica `condition` in scala ordinale 1-4), `correlation_analysis` (Pearson e Spearman con i rispettivi p-value), `correlation_matrix` (heatmap seaborn su tutte le coppie), `pearson_spearman_comparison` (grafico a barre affiancate).

| variabile | Pearson | Spearman | scarto | n |
|---|---|---|---|---|
| `surface_mq` | **0,789** | 0,763 | −0,026 | 16.346 |
| `bathrooms` | 0,623 | 0,646 | +0,023 | 15.502 |
| `rooms` | 0,547 | **0,646** | **+0,100** | 16.240 |
| `floor` | 0,136 | 0,167 | +0,031 | 15.802 |
| `condition_numeric` | **0,051** | 0,115 | +0,064 | 15.759 |

Tutti i coefficienti sono significativi (p < 10⁻¹⁰; per le prime tre il p-value va in underflow e viene stampato come 0.0) — con n ≈ 16.000 la significatività non distingue nulla, come già nella fase 4. Quello che distingue è la magnitudine, e soprattutto **lo scarto fra le due colonne**.

**Dove Pearson e Spearman divergono, e perché**

`rooms` è il caso interessante: **0,547 contro 0,646**, dieci punti di differenza. La causa è nel dato, non nella statistica — `rooms` è troncata in alto, il `5+` della sorgente è stato mappato a 5, quindi un attico da dieci locali e un quadrilocale grande sono lo stesso valore. Pearson, che lavora sui valori, viene penalizzato da questo tetto artificiale e dalle code del prezzo; Spearman, che lavora sui ranghi, ne risente molto meno. La relazione vera fra numero di locali e prezzo è più forte di quanto Pearson dichiari, e il modo di accorgersene è calcolarli entrambi.

`surface_mq` va nella direzione opposta — **0,789 contro 0,763**, l'unico caso in cui Pearson supera Spearman. La relazione prezzo-superficie è genuinamente quasi lineare sui valori, e i grandi immobili di lusso, che stanno in coda su entrambe le variabili, rafforzano Pearson mentre in graduatoria contano quanto qualsiasi altra osservazione. È la conferma bivariata di quanto la fase 7 modellerà.

**`condition` è il risultato negativo della fase**, ed è più informativo di molti positivi: **Pearson 0,051**, cioè una correlazione praticamente nulla fra stato di conservazione e prezzo. Non significa che ristrutturare non paghi — significa che la scala ordinale 1-4 non cattura la relazione. Nel dataset gli immobili `Da ristrutturare` sono sistematicamente **più grandi** (107,6 m² di media contro 90,9 m² degli `Ottimo / Ristrutturato`) e concentrati nei quartieri storici: la penalizzazione per lo stato e il premio per dimensione e posizione si elidono a vicenda, e sul prezzo totale non resta quasi niente. La fase 4, che confrontava `Da ristrutturare` con `Ottimo / Ristrutturato` sul prezzo **al m²**, aveva trovato una differenza netta (984 €/m², d = −0,37). Stessa variabile, due misure diverse, due risposte opposte: è un caso da manuale del perché la variabile dipendente vada scelta prima di interpretare il coefficiente.

**Multicollinearità, in anticipo sulla fase 8**

La heatmap (`charts/correlation_matrix.png`) copre tutte le coppie, e il blocco che conta non è la riga del prezzo ma il triangolo fra i predittori:

| | `surface_mq` | `rooms` | `bathrooms` |
|---|---|---|---|
| `surface_mq` | 1 | **0,751** | **0,726** |
| `rooms` | 0,751 | 1 | **0,710** |
| `bathrooms` | 0,726 | 0,710 | 1 |

Tre variabili correlate fra loro fra 0,71 e 0,75: stanno misurando in gran parte la stessa cosa — quanto è grande l'immobile. È il problema di multicollinearità della fase 8 che diventa visibile per la prima volta, e il motivo per cui quella fase calcola i VIF invece di infilare tutte e tre nel modello e fidarsi. Da notare anche che `rooms` correla con `surface_mq` (0,751) **più forte** di quanto correli con `price` (0,547): il numero di locali dice più sulla metratura che sul prezzo.

`condition_numeric` e `floor` sono invece scorrelate da tutto il resto (|r| ≤ 0,14), il che le rende innocue nel modello multiplo — non spiegano molto, ma non disturbano nessuno.

**Grafici.** `charts/correlation_matrix.png` — heatmap annotata, palette divergente centrata sullo zero, così il blocco caldo dei predittori dimensionali si stacca a colpo d'occhio dalla fascia neutra di `condition` e `floor`. `charts/pearson_spearman_comparison.png` — barre affiancate delle due misure per variabile, dove il divario di `rooms` è di gran lunga il più evidente — ed è anche il grafico che mostra come `rooms` e `bathrooms`, distanti su Pearson, arrivino alla stessa identica correlazione di rango (0,646).

**Correlazione ≠ causalità**, e il progetto ha un esempio concreto invece di uno slogan: `bathrooms` correla con `price` a 0,62, ma aggiungere un secondo bagno a un appartamento a Quarto Oggiaro non lo avvicina a Brera. Il numero di bagni è un *indicatore* di immobili grandi, centrali e costosi — e infatti correla con la superficie (0,726) quasi quanto col prezzo. Il confondente è la dimensione e, soprattutto, la **posizione**: la fase 5 ha appena stabilito che da sola spiega il 55,6% della varianza del prezzo al m². È esattamente il motivo per cui la fase 8 controlla per la zona.

### Phase 7 — Linear Regression

**Fase completata.** Due specificazioni stimate su tutti i **16.346 annunci** (`price` e `surface_mq` sono complete, e il filtro di positività richiesto dal logaritmo non scarta nulla: i minimi sono € 20.240 e 15 m²). Sette funzioni sotto `linear_regression_phase`, tre per il modello semplice e tre per il log-log, ciascuna terna composta da stima, diagnostica dei residui e test di Breusch-Pagan.

**Specificazione 1 — lineare** (`linear_regression`)

```
Price = −215.563 + 8.274 · Surface
```

| | |
|---|---|
| β₁ | **8.273,86** €/m² |
| IC 95% di β₁ | [8.174,99; 8.372,73] |
| t | 164,03 |
| p | < 10⁻³⁰⁰ (stampato 0.0) |
| R² | **0,622** |

Ogni metro quadro aggiuntivo si porta dietro **€ 8.274** di prezzo, e la superficie da sola spiega il **62,2%** della varianza. Il coefficiente va però letto per quello che è: il metro quadro **marginale** costa € 8.274, mentre il metro quadro **medio** del dataset ne costa 5.622 (fase 1). Non è una contraddizione, è la stessa cosa detta due volte — il prezzo al m² cresce con la dimensione, e la specificazione log-log qui sotto lo quantifica.

L'intercetta, **−215.563**, non ha alcuna interpretazione: è il prezzo che il modello attribuirebbe a un immobile di 0 m². Il minimo osservato è 15 m², quindi lo zero sta lontano da qualunque dato e l'intercetta è solo il punto dove la retta incrocia un asse che non descrive nessun immobile esistente. È il classico coefficiente che si riporta e non si interpreta.

**La diagnostica boccia il modello** (`linear_residual_diagnostics`, `breusch_pagan_test`)

Breusch-Pagan: **LM = 2.743,0, p ≈ 0**. `charts/linear_regression_residuals.png` mostra il perché nella forma più didattica possibile: i residui si aprono **a ventaglio** perfetto: attorno a valori stimati di € 200.000 stanno entro poche decine di migliaia di euro, oltre i 4 milioni arrivano a ±6 milioni. La varianza dell'errore non è costante, e l'assunzione di omoschedasticità dell'OLS è violata in modo plateale. Il Q-Q plot dei residui aggiunge la seconda violazione: la classica S, con entrambe le code molto più pesanti della normale.

Le conseguenze sono precise e vale la pena essere espliciti: β₁ = 8.274 **resta corretto** (l'eteroschedasticità non distorce la stima puntuale dell'OLS), ma il suo errore standard no — quindi l'intervallo [8.175; 8.373] e il t = 164 sono inaffidabili. È il motivo per cui la fase 8 userà errori standard robusti HC3.

**Specificazione 2 — log-log** (`log_linear_regression`)

```
log(Price) = 8,136 + 1,0913 · log(Surface)
```

| | |
|---|---|
| β₁ (elasticità) | **1,0913** |
| IC 95% di β₁ | **[1,0786; 1,1041]** |
| t | 167,84 |
| R² | 0,633 |
| Breusch-Pagan | LM = **179,8**, p = 5,3 × 10⁻⁴¹ |

Qui β₁ è un'**elasticità**: a un aumento dell'1% della superficie corrisponde un aumento dell'**1,09%** del prezzo. Il valore interessante non è 1,09 in sé ma il suo confronto con **1**: se il prezzo fosse proporzionale alla superficie — cioè se il prezzo al m² fosse indipendente dalla dimensione — l'elasticità sarebbe esattamente 1. L'intervallo di confidenza, [1,0786; 1,1041], **esclude l'1 con ampio margine**. A Milano gli immobili grandi costano più che proporzionalmente: raddoppiare la superficie fa più che raddoppiare il prezzo. È il risultato della fase, ed è lo stesso fatto che la specificazione lineare esprimeva goffamente con un'intercetta negativa.

**Perché il log-log è preferito, e perché non per l'R²**

I due R², 0,622 e 0,633, **non sono confrontabili**: misurano la varianza spiegata di due variabili dipendenti diverse, `price` e `log(price)`. Metterli in classifica sarebbe un errore, ed è per questo che la preferenza non si argomenta lì.

Si argomenta sui residui. Breusch-Pagan **rifiuta ancora** (p = 5 × 10⁻⁴¹): il log-log non risolve l'eteroschedasticità, la riduce. Ma la statistica LM scende da **2.743 a 180**, un fattore 15, e con n = 16.346 il test rifiuterebbe comunque qualsiasi deviazione anche minima — lo si è già visto con i test di normalità della fase 2. È il confronto fra le due magnitudini a portare l'informazione, non l'esito del test.

E il grafico chiude la questione senza bisogno di statistiche: in `charts/log_linear_regression_residuals.png` il ventaglio è sparito, la nuvola dei residui ha **ampiezza pressoché costante** su tutto l'intervallo dei valori stimati, e il Q-Q plot sta sulla diagonale quasi ovunque — resta solo un lieve scostamento nella coda inferiore. Confrontato con la S marcata del modello lineare, è un'altra categoria di aderenza alle assunzioni.

La seconda specificazione è quindi quella preferita, ed è anche quella direttamente confrontabile con il modello completo della fase 8, che parte da qui e aggiunge regressori.

**Grafico della retta.** `charts/linear_regression.png` — nuvola dei 16.346 punti con la retta OLS sovrapposta, su scala originale. Il ventaglio si vede già qui, prima ancora di guardare i residui.

### Phase 8 — Multiple Linear Regression

```
log(Price) = β₀ + β₁·log(Surface) + β₂·Rooms + β₃·Bathrooms + β₄·Condition
           + β₅·Elevator + β₆·Floor + β₇·Heating + β₈·Luxury + dummy di zona + ε
```

**Fase completata.** Il modello è scritto in forma di formula (`sm.formula.ols`), così `C(macrozone)` e `C(heating)` generano da sole le rispettive dummy: 31 per le macrozone e 2 per il riscaldamento, con la prima categoria in ordine alfabetico come riferimento. Sette funzioni sotto `multiple_regression_phase`.

**Il campione si restringe.** La regressione richiede tutte le variabili contemporaneamente, e la listwise deletion costa **1.707 righe: 16.346 → 14.639**, il 10,4%. È il prezzo cumulato dei mancanti sparsi su `bathrooms` (5,2%), `condition` (3,6%) e `floor` (3,3%) — la stima annunciata nella sezione sulla pulizia, ora misurata. Tutti i numeri di questa fase valgono su quelle 14.639 righe, comprese le due specificazioni della tabella di confronto finale, rifittate sullo stesso sottoinsieme perché AIC e R² siano confrontabili.

**Multicollinearità: niente da rimuovere** (`vif_analysis`)

| variabile | VIF |
|---|---|
| `log_surface` | **4,67** |
| `rooms` | **4,17** |
| `bathrooms` | 2,54 |
| `luxury` | 1,26 |
| `elevator` | 1,11 |
| `floor` | 1,11 |
| `condition_numeric` | 1,06 |

La correlazione fra i tre predittori dimensionali vista nella fase 6 (0,71-0,75) si traduce in VIF di 4,67 e 4,17: alti, vicini alla soglia convenzionale di 5, ma **sotto**. Nessuna variabile viene quindi eliminata, e la tabella serve a documentare una decisione presa sui numeri anziché a giustificarne una già presa. Vale la pena essere espliciti sul significato: un VIF di 4,67 dice che l'errore standard di `log_surface` è √4,67 ≈ 2,2 volte quello che sarebbe con predittori scorrelati. La collinearità non è assente, è tollerata.

**Il modello completo** (`multiple_regression`)

| | coefficiente | p |
|---|---|---|
| `log_surface` | **0,8019** | < 0,001 |
| `luxury` | **0,3642** | < 0,001 |
| `bathrooms` | 0,0893 | < 0,001 |
| `condition_numeric` | 0,0811 | < 0,001 |
| `elevator` | 0,0789 | < 0,001 |
| `floor` | 0,0121 | < 0,001 |
| `rooms` | −0,0018 | **0,593** |
| `heating` autonomo | −0,0035 | **0,779** |
| `heating` centralizzato | −0,0108 | **0,387** |

**R² = 0,9062 · R² adjusted = 0,9059 · AIC = −4.441**

I due R² distano 0,0003 nonostante i ~40 regressori: con n = 14.639 la penalizzazione dell'aggiustamento è minima, e il confronto serve appunto a mostrare che qui il rischio di sovradattamento non si materializza — cosa che con 40 regressori e poche centinaia di osservazioni sarebbe andata diversamente.

Trattandosi di variabile dipendente logaritmica, i coefficienti si leggono come variazioni percentuali approssimate: un bagno in più è associato a un prezzo **+8,9%**, l'ascensore a **+7,9%**, un gradino nella scala di `condition` a **+8,1%**, un piano più in alto a **+1,2%**, il flag `luxury` a **+44%** (qui l'approssimazione lineare non basta più: e^0,3642 − 1 = 0,439).

**L'elasticità della superficie scende da 1,09 a 0,80.** Nella fase 7 `log_surface` era l'unico regressore e assorbiva tutto ciò che correla con la dimensione; qui `bathrooms` e `rooms` sono nel modello e se ne prendono una parte. È lo stesso fenomeno della fase 6 visto dall'altro lato, e il motivo per cui il coefficiente di una regressione semplice e quello di una multipla non sono la stessa quantità: rispondono a domande diverse.

**Che cosa cambia quando si controlla per la zona** (`zone_comparison`)

Lo stesso modello stimato due volte, con e senza le dummy di macrozona:

| | coef senza zona | p senza zona | coef con zona | p con zona |
|---|---|---|---|---|
| `log_surface` | 0,7813 | < 0,001 | 0,8019 | < 0,001 |
| `luxury` | **0,6791** | < 0,001 | **0,3642** | < 0,001 |
| `elevator` | **0,1196** | < 0,001 | **0,0789** | < 0,001 |
| `condition_numeric` | 0,0589 | < 0,001 | 0,0811 | < 0,001 |
| `bathrooms` | 0,0914 | < 0,001 | 0,0893 | < 0,001 |
| `floor` | 0,0027 | 0,008 | 0,0121 | < 0,001 |
| `rooms` | −0,0120 | **0,006** | −0,0018 | **0,593** |
| `heating` centralizzato | −0,0401 | **0,012** | −0,0108 | **0,387** |

**R² adjusted: 0,8458 senza zona → 0,9059 con zona.** Le sole dummy di macrozona aggiungono **6 punti** di varianza spiegata a un modello che ne spiegava già l'85%.

Due predittori **perdono la significatività** nel passaggio, ed è il risultato più istruttivo della fase:

- **`rooms`** passa da p = 0,006 a p = 0,593. A parità di superficie, il numero di locali sembrava dire qualcosa sul prezzo; una volta noto il quartiere non dice più niente. Stava funzionando da indicatore di localizzazione — appartamenti tagliati in molte stanze piccole sono tipici di certe zone — non da caratteristica con un valore proprio.
- **`heating` centralizzato** passa da p = 0,012 a p = 0,387, per la stessa ragione: il riscaldamento centralizzato è una caratteristica dei condomini di certe epoche e certi quartieri.

Altri due si **ridimensionano** senza perdere significatività: `luxury` quasi si dimezza (0,679 → 0,364) e `elevator` cala di un terzo (0,120 → 0,079). Metà del premio "lusso" era, letteralmente, il quartiere.

E uno va nella direzione opposta: **`floor` quadruplica** (0,0027 → 0,0121) e passa da p = 0,008 a p < 0,001. Senza controllo di zona l'effetto del piano era mascherato — i palazzi alti stanno tanto nei quartieri più cari quanto nelle periferie di edilizia popolare, e i due gruppi si annullavano a vicenda. È il caso in cui il controllo non riduce un effetto ma lo **rivela**.

**Errori standard robusti** (`robust_standard_errors`)

Lo stesso modello rifittato con `cov_type='HC3'`. Gli errori standard salgono, come atteso dopo il Breusch-Pagan della fase 7: per `log_surface` da 0,0072 a **0,0091** (+26%), per l'intercetta da 0,0285 a 0,0385 (+35%). Le variabili con coefficienti forti non si spostano di una virgola nelle conclusioni, e i due `heating` — già non significativi — lo diventano ancora di più (p da 0,779 a 0,841). **Nessuna conclusione della fase dipende dalla scelta fra errori standard classici e robusti**, e questa è l'informazione che l'analisi doveva produrre: non che gli HC3 siano migliori in astratto, ma che qui non cambiano la risposta.

**Residui** (`multiple_residual_diagnostics`) — `charts/multiple_regression_residuals.png`

La nuvola dei residui contro i valori stimati ha ampiezza sostanzialmente costante da log-prezzo 12 a 15, senza traccia del ventaglio della fase 7. Il Q-Q plot sta sulla diagonale per tutta la parte centrale con uno scostamento nella coda sinistra: un gruppo di immobili che il modello sopravvaluta nettamente, cioè annunci molto più economici di quanto le loro caratteristiche e la loro zona facciano prevedere. Sono poche decine di casi su 14.639 e non minacciano le stime, ma sono l'unico residuo di struttura non spiegata rimasto.

**Confronto fra modelli** (`model_comparison`)

| modello | R² adjusted | AIC |
|---|---|---|
| log-log semplice | 0,6554 | 14.531,0 |
| multiplo completo | **0,9059** | **−4.441,2** |

Entrambi stimati sulle stesse 14.639 righe e sulla stessa variabile dipendente `log_price`: è la condizione perché il confronto abbia senso, ed è il motivo per cui il modello lineare della fase 7 **non compare in tabella** — la sua dipendente è `price`, e un AIC calcolato su una scala diversa non è confrontabile. Il salto è netto su entrambi i criteri: la varianza spiegata passa dal 66% al 91%, e i circa 19.000 punti di AIC in meno dicono che l'aggiunta dei regressori paga ampiamente il costo della complessità.

**Una promessa che i dati non consentono di mantenere.** Le versioni precedenti di questo README prevedevano un'analisi di sensibilità su `elevator`, da condurre rifittando il modello sul "sottoinsieme delle 13.572 righe col campo effettivamente compilato". Quel test **non è eseguibile**: nella sorgente `elevator` vale `1.0` oppure `NaN`, mai `0`, quindi il sottoinsieme con il campo compilato contiene solo immobili *con* ascensore. Senza variazione il coefficiente non è identificabile e la variabile verrebbe scartata dalla stima. Il ragionamento sulla codifica resta valido — l'errore di classificazione può solo attenuare β verso lo zero, quindi 0,0789 è semmai una sottostima — ma è un'argomentazione, non una verifica empirica, e viene qui dichiarata come tale.

### Phase 9 — Statistical Conclusions

Non *"le case più grandi costano di più"*, ma affermazioni della forma:

> La superficie presenta una relazione positiva e statisticamente significativa con il prezzo (β = …, p < 0,001). Dopo aver controllato per le altre caratteristiche dell'immobile **e per la zona**, la superficie rimane una delle variabili maggiormente associate al prezzo, con un'elasticità stimata di … — un aumento dell'1% della superficie è associato a un aumento del …% del prezzo, a parità di tutto il resto.

La fase raccoglie: i predittori significativi con la loro dimensione d'effetto e i relativi intervalli di confidenza; i predittori che risultano **non** significativi una volta controllata la zona; la quota di varianza del prezzo attribuibile alla posizione; e i limiti dell'analisi, dichiarati senza giri di parole —

- si tratta di **prezzi richiesti**, non di prezzi di transazione, e a Milano lo scarto fra richiesta e rogito è reale;
- gli annunci sono un'**istantanea**, quindi niente di quanto qui affermato riguarda un andamento nel tempo;
- tutto è **associativo**. Nessuna pretesa causale viene avanzata, e nessuna è ottenibile da questo disegno.

### Phase 10 — Mappa del prezzo medio al m² per zona

Il deliverable finale. File di riferimento: **`milano-heatmap.html`**.

La mappa esistente porta già la struttura che l'analisi deve riempire: un unico blocco JSON incorporato (`<script type="application/json" id="D">`) che contiene

| Chiave | Contenuto |
|---|---|
| `bbox`, `nx`, `ny`, `cell` | bounding box e una **griglia 133 × 118 di celle da 140 m** |
| `grid` | 15.694 celle, `-1` dove non ci sono dati |
| `zones` | **88 poligoni** (i NIL di Milano — *Nuclei d'Identità Locale*) con `n`, `med`, `p25`, `p75`, `mp`, `ms` e la geometria |
| `pts` | 16.384 annunci singoli come `[lat, lon, price_per_mq]` |
| `stats`, `hist` | riepilogo globale e istogramma della distribuzione |

La pipeline per rigenerarlo:

1. partire dal dataset pulito, ristretto ai **16.333 annunci geolocalizzati**;
2. assegnare ogni annuncio a una zona per **point-in-polygon** su `lat`/`lon` — *non* per corrispondenza della stringa `microzone`, dato che le 144 microzone e le 32 macrozone del CSV non coincidono con gli 88 NIL della mappa;
3. aggregare `price_per_mq` per zona: **n, media, mediana, p25, p75**;
4. sopprimere le zone sotto un numero minimo di annunci invece di colorarle a partire da 3 osservazioni, e dichiarare in legenda quante ne sono state soppresse;
5. riemettere il blocco JSON e colorare i poligoni sull'aggregato.

**Media o mediana?** La richiesta è il prezzo *medio* al m², ed è la media che viene riportata. Ma la fase 1 ha già stabilito che queste distribuzioni sono asimmetriche a destra, e la mappa attuale è costruita sulla **mediana** proprio per questo. La mappa mostra quindi **entrambe**: mediana come scala cromatica (robusta, confrontabile fra zone con numerosità molto diverse) e media accanto, nel tooltip — con lo scarto fra le due che è informativo di per sé: un divario media-mediana ampio segnala una zona con pochi immobili molto costosi più che una zona uniformemente cara. È il risultato della fase 1 applicato al deliverable, non ripetuto a parole.

---

## Avanzamento

| Fase | Stato |
|---|---|
| 0. Pulizia dei dati | ✅ **completata** — 18.017 → 16.346 annunci |
| 1. Descriptive Statistics | ✅ **completata** — tabella statistiche + box plot |
| 2. Probability & Distributions | ✅ **completata** — istogrammi, Q-Q plot, percentili, indici di forma, log |
| 3. Sampling & Confidence Intervals | ✅ **completata** — CLT verificato, copertura misurata |
| 4. Hypothesis Testing | ✅ **completata** — 4 test di Welch con effect size e IC |
| 5. ANOVA | ✅ **completata** — η² = 0,556, Welch, Tukey, diagnostica |
| 6. Correlation | ✅ **completata** — Pearson vs Spearman, heatmap, multicollinearità |
| 7. Linear Regression | ✅ **completata** — semplice e log-log, elasticità 1,09 |
| 8. Multiple Linear Regression | ✅ **completata** — R² adj = 0,906, VIF, dummy di zona, HC3 |
| 9. Statistical Conclusions | 🟡 **prossima fase** |
| 10. Mappa del prezzo medio al m² per zona | ⬜ da fare — mappa di riferimento già disponibile |

---

## Struttura del progetto

```
milano_real_estate_analysis/
├── milano_analysis.py                  # script di analisi — pulizia + fasi 1-8
├── immobiliare_milano_vendita.csv      # dataset (18.017 × 31)
├── milano_zone_NIL.geojson             # 88 poligoni NIL — input della fase 10
├── milano-heatmap.html                 # mappa per zona — output della fase 10
├── charts/                             # figure delle fasi 1-8 in PNG (14 file)
├── REPORT.md                           # resoconto dei risultati — da scrivere
└── README.md
```

Dataset, geometrie e mappa sono già nella cartella: lo script di analisi può usare percorsi relativi.

Ogni funzione grafica salva il PNG in `charts/` con `plt.savefig(..., dpi=150)` e poi lo mostra a schermo con `plt.show()` — in quest'ordine, perché `show()` svuota la figura e dopo di lui non resterebbe niente da salvare. I file prodotti finora sono `boxplots.png` (fase 1), `histograms.png`, `qq_plots.png`, `normal_distribution.png`, `log_comparison.png` (fase 2) , `sampling_distributions.png` (fase 3) , `anova_residuals.png` + `macrozone_boxplots.png` (fase 5) , `correlation_matrix.png` + `pearson_spearman_comparison.png` (fase 6) e `linear_regression.png` + `linear_regression_residuals.png` + `log_linear_regression_residuals.png` (fase 7) e `multiple_regression_residuals.png` (fase 8); lo script va lanciato dalla cartella del progetto, dato che il percorso è relativo come quello del CSV.

La pipeline, nell'ordine in cui viene eseguita in `milano_analysis.py`:

```
# pulizia
inspect_data              → info, shape, describe, mancanti, duplicati sul file grezzo
inspect_categorical       → value_counts delle variabili categoriali
remove_subunits           → filtro unit == 0                        18.017 → 16.741
inspect_quality_variables → controllo dei flag prima di filtrare
apply_quality_filters     → category / is_outlier / price_is_range  16.741 → 16.346
inspect_missing_values    → conferma: price, surface_mq, price_per_mq completi
encode_elevator           → NaN → 0, dummy 0/1
inspect_text_variables    → forma reale di rooms, bathrooms, floor prima del parsing
parse_text_variables      → da stringa a numerico
validate_clean_data       → shape, mancanti, duplicati, dtype, distribuzioni finali

# fase 1
descriptive_statistics    → tabella 13 statistiche × 3 variabili
plot_boxplots             → box plot di price, surface_mq, price_per_mq

# fase 2
plot_hist                 → istogrammi con media e mediana marcate
plot_qq                   → Q-Q plot contro la normale
percentile_statistics     → tabella 9 percentili × 3 variabili
distribution_shape        → asimmetria e curtosi × 3 variabili
plot_normal_distribution  → istogrammi in densità + curva normale sovrapposta
log_transform             → asimmetria e curtosi di log(price)
plot_log_comparison       → price contro log(price), affiancati, con curva normale

# fase 3
population_parameters     → μ e σ (ddof=0) di price_per_mq sulla popolazione
draw_sample               → 1.000 campioni per n = 30/100/500, istogrammi + SE empirico vs teorico
confidence_intervals      → 1.000 intervalli t al 95% per ciascun n, copertura misurata

# fase 4
two_sample_test           → helper: Levene, Welch, df, IC 95% della differenza, d di Cohen
hypothesis_testing        → i 4 confronti (2 coppie di zone, elevator, condition)

# fase 5 — orchestrate da anova_phase
anova_analysis            → F, gradi di libertà, p, η² calcolato dalle devianze
welch_anova               → Levene su 32 gruppi + ANOVA di Welch
residual_diagnostics      → OLS price_per_mq ~ C(macrozone), residui e Q-Q plot
tukey_posthoc             → Tukey HSD su 496 coppie, significative ordinate per scarto
plot_macrozone_boxplots   → box plot delle 32 zone ordinate per mediana

# fase 6 — orchestrate da correlation_phase
prepare_correlation_data  → condition → scala ordinale 1-4 (condition_numeric)
correlation_analysis      → Pearson e Spearman con price, variabile per variabile
correlation_matrix        → matrice 6 × 6 + heatmap seaborn
pearson_spearman_comparison → barre affiancate delle due misure

# fase 7 — orchestrate da linear_regression_phase
linear_regression         → OLS price ~ surface_mq: β, R², t, p, IC 95%
plot_linear_regression    → nuvola dei punti con la retta stimata
linear_residual_diagnostics → residui vs stimati + Q-Q plot dei residui
breusch_pagan_test        → LM, p, F sul modello lineare
log_linear_regression     → OLS log(price) ~ log(surface): elasticità
log_residual_diagnostics  → stessa diagnostica sul modello log-log
log_breusch_pagan_test    → LM, p, F sul modello log-log

# fase 8 — orchestrate da multiple_regression_phase
prepare_regression_data   → log_price, log_surface, dropna sulle variabili del modello
vif_analysis              → VIF dei sette predittori numerici
multiple_regression       → modello completo: R², R² adj, AIC, coefficienti
zone_comparison           → stesso modello con e senza dummy di zona, affiancati
robust_standard_errors    → HC3 contro errori standard classici
multiple_residual_diagnostics → residui vs stimati + Q-Q plot
model_comparison          → log-log semplice contro completo, sulle stesse righe
```

Ogni trasformazione è preceduta dalla sua ispezione: si guarda com'è fatta la colonna, poi la si tocca. È il motivo per cui il passaggio 2 e il passaggio 3 sono risultati in gran parte a vuoto senza che ce ne accorgessimo troppo tardi.

### Strumenti

`pandas` e `numpy` per il lavoro sui dati (`numpy` già in uso per la trasformazione logaritmica della fase 2), `scipy.stats` per le fasi 2-6 (già in uso per il Q-Q plot, per le curve normali sovrapposte agli istogrammi e per i valori critici *t* della fase 3), `statsmodels` per le fasi 5, 7 e 8 — in uso con `statsmodels.api`, `anova_oneway`, `pairwise_tukeyhsd`, `het_breuschpagan` e `variance_inflation_factor` —, `matplotlib` per i grafici e `seaborn` per la sola heatmap della fase 6.

**Perché statsmodels e non scikit-learn.** Il progetto è un esercizio di **inferenza statistica** — stimare quantità della popolazione a partire da un campione e quantificare l'incertezza che le circonda. Ogni fase dalla 3 in poi ha bisogno di errori standard, statistiche test, p-value e intervalli di confidenza, non solo di valori stimati.

Le due librerie stimano lo stesso modello OLS e restituiscono gli stessi coefficienti, ma sono costruite per domande diverse:

| | `scikit-learn` | `statsmodels` |
|---|---|---|
| Coefficienti β, R² | ✅ | ✅ |
| Errori standard di β | ❌ | ✅ |
| Statistica t e p-value per coefficiente | ❌ | ✅ |
| Intervallo di confidenza per β | ❌ | ✅ |
| R² adjusted, AIC/BIC, test F sul modello | ❌ | ✅ |
| Breusch-Pagan, Durbin-Watson, VIF, Tukey HSD | ❌ | ✅ |
| Errori standard robusti (HC3) | ❌ | ✅ |
| Previsione su dati nuovi, cross-validation, regolarizzazione | ✅ | limitata |

scikit-learn è una libreria di **previsione**: ottimizza l'accuratezza fuori campione e lascia fuori di proposito l'apparato inferenziale, perché per prevedere la verifica onesta è l'errore su dati non visti, non un p-value. (Fonte di confusione: nel mondo del machine learning "inference" indica la cosa opposta — eseguire un modello già addestrato per produrre previsioni.)

`sm.OLS(y, X).fit().summary()` stampa in una sola chiamata la tabella dei coefficienti con errori standard, *t*, *p* e intervallo al 95% — quella tabella **è** l'output delle fasi 7 e 8. Una frase da fase 9 del tipo *"positiva e statisticamente significativa (β = …, p < 0,001) dopo aver controllato per le altre caratteristiche"* non è qualcosa che scikit-learn possa produrre.
