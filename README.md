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

Il rischio residuo della codifica scelta è che qualche immobile abbia davvero l'ascensore senza che il campo sia compilato. Quei casi finiscono etichettati come "senza" e **attenuano** β₅ verso lo zero: la stima dell'effetto risulta più piccola del vero, mai più grande. È un errore conservativo. La fase 8 lo verifica con un'analisi di sensibilità esplicita (vedi sotto) anziché limitarsi a dichiarare l'assunzione.

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

La regressione della fase 8 usa `rooms`, `bathrooms`, `condition` e `floor` insieme: a listwise deletion la perdita cumulata va stimata prima di fissare la specificazione, ed è una decisione che appartiene a quella fase.

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
| 30 | € 478,0 | € 482,8 |
| 100 | € 259,2 | € 264,4 |
| 500 | € 111,9 | € 118,3 |

Le due colonne coincidono a meno di pochi euro, e la dispersione si dimezza passando da n = 100 a n = 500 quasi esattamente del fattore √5 previsto — su una popolazione con asimmetria 1,83, dove la singola osservazione non è affatto normale. L'istogramma delle medie campionarie è invece simmetrico e campanulare già a n = 30: è il CLT che si vede, non che si cita.

Lo scarto sistematico del SE empirico verso il basso (sempre un po' sotto il teorico, e la cosa si accentua a n = 500) non è rumore: i campioni sono estratti **senza reinserimento** da una popolazione finita, quindi il termine di riferimento esatto è σ/√n corretto per il fattore di popolazione finita √((N−n)/(N−1)), che a n = 500 porta il valore teorico da € 118,3 a € 116,4. Il confronto resta impostato sulla formula standard, perché è quella la formula di cui la fase discute.

**Copertura degli intervalli**

| n | copertura osservata |
|---|---|
| 30 | ~93% |
| 100 | ~94-95% |
| 500 | ~95-96% |

Il risultato più istruttivo della fase è la riga n = 30. La copertura nominale è 95%, ma a n = 30 gli intervalli ne coprono sistematicamente **~93%** — verificato su ripetizioni indipendenti, non è un caso singolo. L'intervallo *t* assume una popolazione normale; qui la popolazione ha asimmetria 1,83 e a n = 30 il CLT non ha ancora finito il suo lavoro, così l'intervallo mantiene meno di quanto promette. A n = 100 e n = 500 la copertura risale a ~95%, come deve. Il livello di confidenza è una proprietà **della procedura sotto le sue assunzioni**, non una garanzia che valga a qualunque numerosità: quando l'assunzione è violata la procedura sotto-copre, e il modo di accorgersene è misurarlo.

**Nota sulla riproducibilità:** non è fissato alcun seme casuale, quindi i numeri di copertura cambiano di qualche decimo a ogni esecuzione (l'errore Monte Carlo su 1.000 ripetizioni vale circa ±0,7 punti). I valori qui sopra sono riportati come intervalli per questo motivo. Un `random_state` fisso renderebbe la tabella riproducibile alla cifra.

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

L'estensione naturale della fase 4 a tutte e **32 le macrozone** insieme.

> **H₀**: μ₁ = μ₂ = … = μ₃₂ — il prezzo medio al m² è uguale in ogni zona di Milano
> **H₁**: almeno una zona differisce

- **ANOVA a una via** su `price_per_mq` per `macrozone`: statistica F, gradi di libertà (31; 16.314), p-value, η² come quota di varianza spiegata dalla sola localizzazione.
- **Verifica delle assunzioni**: test di Levene per l'omogeneità delle varianze e diagnostica dei residui. A Milano le varianze fra zone sono visibilmente disomogenee, quindi accanto all'ANOVA classica si esegue una **ANOVA di Welch** e le due si confrontano.
- **Post-hoc**: **Tukey HSD** su tutte le 496 coppie, con le coppie significative riassunte anziché riversate in tabella, più la motivazione della correzione — 496 t-test non corretti ad α = 0,05 produrrebbero per costruzione ~25 falsi positivi.
- Un box plot di `price_per_mq` per macrozona, ordinato per mediana, come controparte visiva del test.

### Phase 6 — Correlation

Relazioni bivariate con `price`:

| Relazione | Nota |
|---|---|
| `surface_mq` ↔ `price` | la principale |
| `rooms` ↔ `price` | fortemente collineare con la superficie |
| `bathrooms` ↔ `price` | idem |
| `condition` ↔ `price` | ordinale (`Da ristrutturare` < `Buono / Abitabile` < `Ottimo / Ristrutturato` < `Nuovo / In costruzione`) → Spearman |
| `floor` ↔ `price` | secondaria |

**Si riportano sia Pearson sia Spearman.** Con variabili così asimmetriche Pearson viene tirato dai valori estremi, mentre Spearman usa solo i ranghi; quando i due divergono, la divergenza è essa stessa il risultato. Una matrice di correlazione / heatmap copre tutte le coppie in un colpo solo — comprese le correlazioni fra predittori, dove il problema di multicollinearità della fase 8 diventa visibile per la prima volta.

**Correlazione ≠ causalità**, e il progetto ha un esempio concreto invece di uno slogan: `bathrooms` correla con `price`, ma aggiungere un secondo bagno a un appartamento a Quarto Oggiaro non lo avvicina a Brera. Il numero di bagni è un *indicatore* di immobili grandi, centrali e costosi. Il confondente è la dimensione e, soprattutto, la **posizione** — ed è esattamente il motivo per cui la fase 8 controlla per la zona.

### Phase 7 — Linear Regression

```
Price = β₀ + β₁ · Surface + ε
```

- Coefficienti stimati, con **β₁ letto nelle sue unità**: euro di prezzo per metro quadro aggiuntivo.
- **R²** — quanta varianza del prezzo è spiegata dalla sola superficie.
- **p-value e statistica t** su β₁, più il suo intervallo di confidenza.
- **Analisi dei residui**: residui contro valori stimati, Q-Q plot dei residui e **test di Breusch-Pagan** per l'eteroschedasticità. I residui si apriranno a ventaglio — la dispersione del prezzo attorno alla retta cresce con la superficie — il che viola l'assunzione di varianza costante dell'OLS.
- Il rimedio, e seconda specificazione della fase:

```
log(Price) = β₀ + β₁ · log(Surface) + ε
```

Qui β₁ è un'**elasticità** — la variazione percentuale del prezzo per una variazione dell'1% della superficie — i residui si comportano bene, e il modello è direttamente confrontabile con quello della fase 8. Si riportano entrambe le specificazioni, con la motivazione della preferenza per la seconda.

### Phase 8 — Multiple Linear Regression

```
log(Price) = β₀ + β₁·log(Surface) + β₂·Rooms + β₃·Bathrooms + β₄·Condition
           + β₅·Elevator + β₆·Floor + β₇·Heating + β₈·Luxury + dummy di zona + ε
```

- **Multicollinearità** e **VIF**. `surface_mq`, `rooms` e `bathrooms` misurano cose che si sovrappongono, e i loro VIF lo mostreranno. La fase riporta la tabella dei VIF, elimina o accorpa ciò che supera la soglia convenzionale di 5, e mostra l'effetto della rimozione sui coefficienti — il punto essendo che la collinearità gonfia gli errori standard e destabilizza i coefficienti senza intaccare l'R².
- **Dummy di zona**. Le 32 macrozone entrano come variabili dummy con una categoria di riferimento, ed è ciò che rende possibile la conclusione della fase 9: separa "questo appartamento è caro perché è grande" da "questo appartamento è caro perché è a Brera".
- **R² adjusted** contro R² semplice, e il motivo per cui la correzione serve quando in gioco ci sono ~40 regressori.
- **Significatività di ogni coefficiente**, segnalando esplicitamente quelli che perdono significatività nel momento in cui si controlla per la zona.
- **Analisi dei residui** sul modello completo, più **errori standard robusti (HC3)**.
- **Analisi di sensibilità su `elevator`.** Il modello viene stimato due volte: una con la dummy 0/1 su tutte le righe (la scelta di pulizia adottata) e una sul solo sottoinsieme di **13.572 righe col campo effettivamente compilato**. Se β₅ e la sua significatività non si muovono, la codifica non incide e lo si dichiara; se si muovono, lo scarto è a sua volta un risultato da riportare. È la differenza fra un'assunzione dichiarata e un'assunzione verificata.
- **Tabella di confronto fra modelli**: semplice → log-log → modello completo, su R² adjusted, AIC e comportamento dei residui.

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
| 5. ANOVA | 🟡 **prossima fase** |
| 6. Correlation | ⬜ da fare |
| 7. Linear Regression | ⬜ da fare |
| 8. Multiple Linear Regression | ⬜ da fare |
| 9. Statistical Conclusions | ⬜ da fare |
| 10. Mappa del prezzo medio al m² per zona | ⬜ da fare — mappa di riferimento già disponibile |

---

## Struttura del progetto

```
milano_real_estate_analysis/
├── milano_analysis.py                  # script di analisi — pulizia + fasi 1-4
├── immobiliare_milano_vendita.csv      # dataset (18.017 × 31)
├── milano_zone_NIL.geojson             # 88 poligoni NIL — input della fase 10
├── milano-heatmap.html                 # mappa per zona — output della fase 10
├── charts/                             # figure delle fasi 1-3 in PNG (6 file)
├── REPORT.md                           # resoconto dei risultati — da scrivere
└── README.md
```

Dataset, geometrie e mappa sono già nella cartella: lo script di analisi può usare percorsi relativi.

Ogni funzione grafica salva il PNG in `charts/` con `plt.savefig(..., dpi=150)` e poi lo mostra a schermo con `plt.show()` — in quest'ordine, perché `show()` svuota la figura e dopo di lui non resterebbe niente da salvare. I file prodotti finora sono `boxplots.png` (fase 1), `histograms.png`, `qq_plots.png`, `normal_distribution.png`, `log_comparison.png` (fase 2) e `sampling_distributions.png` (fase 3); lo script va lanciato dalla cartella del progetto, dato che il percorso è relativo come quello del CSV.

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
```

Ogni trasformazione è preceduta dalla sua ispezione: si guarda com'è fatta la colonna, poi la si tocca. È il motivo per cui il passaggio 2 e il passaggio 3 sono risultati in gran parte a vuoto senza che ce ne accorgessimo troppo tardi.

### Strumenti

`pandas` e `numpy` per il lavoro sui dati (`numpy` già in uso per la trasformazione logaritmica della fase 2), `scipy.stats` per le fasi 2-6 (già in uso per il Q-Q plot, per le curve normali sovrapposte agli istogrammi e per i valori critici *t* della fase 3), `statsmodels` per le fasi 5, 7 e 8 — l'import è ancora commentato in cima allo script e va riattivato alla fase 5 — e `matplotlib` per i grafici.

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
