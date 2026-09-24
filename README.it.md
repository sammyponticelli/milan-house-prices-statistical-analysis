# Milano Real Estate — Analisi Statistica

> 🇬🇧 English version: **[README.md](README.md)**

> 🗺️ **[Esplora la mappa 3D interattiva →](https://sammyponticelli.github.io/milan-house-prices-statistical-analysis/)** — si apre nel browser, non serve scaricare nulla.

**Quali fattori influenzano il prezzo delle case a Milano, e cosa può dirci l'analisi statistica sul mercato immobiliare?**

L'analisi lavora su ~18k annunci di vendita raccolti da immobiliare.it e percorre l'intero strumentario statistico — dalla statistica descrittiva alla regressione lineare multipla — per arrivare a una **mappa interattiva del prezzo per zona**, in [`index.html`](https://sammyponticelli.github.io/milan-house-prices-statistical-analysis/).

Il resoconto dei risultati, in forma leggibile senza conoscenze statistiche, è in **[REPORT.it.md](REPORT.it.md)**. Questo file documenta i dati, il metodo e le decisioni tecniche.

---

## Dataset

`immobiliare_milano_vendita.csv` — **18.017 righe × 31 colonne**, annunci di vendita residenziale a Milano.

**Data di estrazione: 26 agosto 2026.** La data non è desumibile dal CSV, che non contiene colonne temporali; la fonte è il campo `fonte_prezzi` del GeoJSON, che riporta `Immobiliare.it, estrazione 2026-08-26`, coerente sia con la data di modifica del file sia con il primo commit del repository. Tutto il progetto è quindi una sezione trasversale riferita a un solo giorno: nessuna analisi temporale è possibile, e nessuna viene tentata.

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
| `nil_id`, `nil` | float / stringa | NIL di appartenenza, **88 distinti** — è la chiave di aggancio della mappa della fase 10, e i suoi id combaciano esattamente con quelli del GeoJSON |
| `lat`, `lon`, `has_geo` | float / int | Coordinate; 16.727 annunci sono geolocalizzati — usate per i centri di zona della mappa |

### Variabili non usate nell'analisi statistica

| Variabile | Descrizione |
|---|---|
| `id`, `unit` | Identificativo dell'annuncio e indice della sotto-unità (vedi sotto) |
| `url`, `title`, `address` | Testo libero / identificativi |
| `city`, `region` | Costanti (`Milano` / `Lombardia`) |
| `category` | `Residenziale` (16.469), `Nuove costruzioni` (137), `Palazzi - Edifici` (135) — usata come **filtro**, non come variabile |
| `agency` | Agenzia venditrice (569 mancanti) — possibile estensione, fuori dal modello principale |
| `is_outlier`, `price_is_range` | Flag di qualità già presenti nella sorgente — usati come **filtri** |

---

## Pulizia dei dati

**Fase completata.** La pulizia si è tradotta in cinque decisioni, tutte prese prima di calcolare qualunque statistica. Ciascuna è implementata in `milano_analysis.py` come una funzione a sé, e ogni passaggio stampa il conteggio delle righe prima e dopo, in modo che la cascata dei filtri resti ispezionabile invece di essere soltanto dichiarata.

**1. Eliminare le sotto-unità.** Gli annunci multi-unità, cioè i progetti di nuova costruzione, compaiono nel file come una riga padre con `unit = 0` seguita da una riga per ciascun appartamento con `unit = 1, 2, 3…`, e tutte queste righe ripetono lo stesso identico `price`: in un caso si arriva a trentasei sotto-unità per un unico prezzo. Il filtro `unit == 0` ne rimuove 1.276, portando il dataset da 18.017 a 16.741 righe. Va detto che le righe delle sotto-unità non hanno il campo `category` valorizzato, quindi il filtro successivo le rimuoverebbe comunque; il filtro esplicito su `unit` viene mantenuto perché tiene l'intenzione visibile nel codice, anziché affidarla a un effetto collaterale di un altro passaggio.

**2. Applicare i flag di qualità della sorgente.** I filtri sono tre e vanno applicati in cascata; è proprio la cascata, più che i singoli filtri, a rivelare qualcosa sui dati.

| Filtro | Righe rimaste | Rimosse |
|---|---|---|
| dopo `unit == 0` | 16.741 | — |
| `category == 'Residenziale'` | 16.469 | 272 (`Nuove costruzioni` 137, `Palazzi - Edifici` 135) |
| `is_outlier == 0` | 16.346 | 123 |
| `price_is_range == 0` | 16.346 | **0** |

Sul file grezzo questi flag marcano 1.567 outlier e 1.321 prezzi espressi come intervallo, ma la quasi totalità di queste righe è già stata eliminata dai filtri precedenti. Gli annunci con prezzo a intervallo sono infatti, per costruzione, i progetti multi-unità, e dopo i primi due filtri non ne sopravvive nemmeno uno. Il filtro `price_is_range` posto a valle non scarta quindi nulla, e resta nel codice come verifica esplicita anziché come passaggio attivo. È un caso in cui il risultato atteso, circa 1.300 righe da scartare, e quello reale, zero, divergono completamente: la spiegazione della divergenza vale più del numero in sé.

**3. Scartare le righe senza prezzo o superficie.** Le tre variabili `price`, `surface_mq` e `price_per_mq` sono quelle da cui dipende tutto il resto dell'analisi. Nel file grezzo mancano rispettivamente in 50, 29 e 79 righe, ma dopo i filtri di qualità i valori mancanti sono zero per tutte e tre, perché anche in questo caso i buchi erano concentrati nelle righe già rimosse. Il passaggio si è quindi ridotto a un controllo di conferma.

**4. La colonna `elevator`, dove il valore mancante significa "no".** Nel file grezzo questa colonna assume soltanto due valori, `1.0` in 13.572 righe e `NaN` nelle restanti 4.445, senza che compaia mai uno zero esplicito. Non si tratta quindi di una colonna con dei buchi, ma di una codifica a sola presenza: il campo viene scritto solo quando l'annuncio dichiara l'ascensore. Viene perciò ricodificata in una variabile dummy 0/1 pulita, che sul dataset filtrato conta 12.367 immobili con ascensore e 3.979 senza.

L'alternativa, cioè trattare i `NaN` come dato mancante vero, comporterebbe l'esclusione automatica di 4.445 annunci, il 27% del dataset, dalla regressione della fase 8. Sarebbe per giunta un'esclusione tutt'altro che casuale, perché gli annunci con il campo vuoto sono sistematicamente immobili più vecchi, più piccoli e più periferici, cioè proprio il segmento che serve per stimare l'effetto dell'ascensore. Si perderebbero i dati e allo stesso tempo si introdurrebbe una distorsione, invece di evitarla.

Il rischio residuo della codifica scelta è che qualche immobile abbia davvero l'ascensore senza che il campo sia stato compilato. Quei casi finiscono etichettati come "senza" e hanno l'effetto di attenuare β₅ verso lo zero, il che significa che la stima dell'effetto risulta più piccola del vero e mai più grande. Si tratta quindi di un errore conservativo, e la fase 8 stima β₅ = 0,0789 sapendo che è semmai una sottostima. Una verifica empirica di questa assunzione non è però possibile, per una ragione spiegata nella fase 8 che discende a sua volta dalla codifica a sola presenza.

**5. Convertire le colonne testuali in numeriche.** Tre colonne arrivano dalla sorgente come stringhe e vanno tradotte in numeri.

- `rooms` — `5+` → 5 (609 righe), gli intervalli tipo `2 - 4` vengono scartati per regex, ma sul dataset filtrato **non ne resta nessuno**: comparivano solo sulle righe multi-unità, già rimosse al passaggio 1. Nessuna riga persa qui.
- `bathrooms` — `3+` → 3 (313 righe).
- `floor` — normalizzato a minuscolo, poi `piano terra` → 0 (2.035 righe) e `piano rialzato` → 0,5 (1.267 righe); per il resto si estrae il primo numero, così `3 piano` → 3.

Il risultato complessivo della pulizia è di 16.346 annunci utilizzabili, pari al 90,7% del file grezzo, dei quali 16.333 dotati di zona di appartenenza. Tutte e 32 le macrozone sopravvivono ai filtri con almeno 115 annunci ciascuna, il che è sufficiente per i confronti fra gruppi delle fasi 4 e 5 senza dover accorpare categorie. Non risultano righe duplicate.

### Mancanti residui sul dataset pulito

Le tre variabili portanti sono complete, mentre ciò che resta scoperto riguarda le variabili di contorno. Questi mancanti vanno gestiti in fase di modellazione anziché a monte, perché eliminare adesso le righe incomplete significherebbe perderle anche per tutte le analisi che quelle variabili non le usano.

| Variabile | Mancanti | Quota | Nota |
|---|---|---|---|
| `bathrooms` | 844 | 5,2% | rilevante per la fase 8 |
| `condition` | 587 | 3,6% | idem |
| `floor` | 544 | 3,3% | testo non riconducibile a un numero |
| `bedrooms` | 444 | 2,7% | fuori dal modello principale |
| `rooms` | 106 | 0,6% | |
| `lat` / `lon` / `nil` | 13 | 0,1% | escluse dalla mappa della fase 10 |
| `microzone` | 57 | 0,3% | `macrozone` ne manca solo 12 |

La regressione della fase 8 usa `rooms`, `bathrooms`, `condition` e `floor` contemporaneamente, e la perdita cumulata dovuta all'eliminazione delle righe incomplete è risultata di 1.707 righe, il 10,4% del totale: il modello completo gira quindi su 14.639 annunci. I mancanti delle diverse colonne si sovrappongono solo in parte, e questo spiega perché il costo complessivo sia inferiore alla somma delle singole quote ma superiore alla più grande di esse.

Resta infine un'anomalia da tenere d'occhio: la colonna `floor` contiene un valore pari a 41 in una singola riga. A Milano un quarantunesimo piano è implausibile, quindi il caso va ispezionato prima della fase 7, dove i residui diventano oggetto di analisi. Gli altri valori estremi, 19 e 21, sono invece compatibili con le torri di Porta Nuova e CityLife.

---

## Struttura dell'analisi

### Phase 1 — Descriptive Statistics

**Fase completata.** La funzione `descriptive_statistics` calcola media, mediana, moda, varianza, deviazione standard, minimo, massimo, quartili, scarto interquartile, range, coefficiente di variazione e asimmetria sulle tre variabili centrali — `price`, `surface_mq` e `price_per_mq` — e le raccoglie in un'unica tabella. A corredo, `plot_boxplots` produce un box plot per ciascuna delle tre, che rende visibile la stessa asimmetria dichiarata dai numeri: il baffo superiore è lunghissimo e oltre il terzo quartile si addensa una nuvola fitta di punti.

Il punto della fase, però, non sta nei singoli numeri ma nel confronto fra le tre variabili.

| | media | mediana | CV | asimmetria |
|---|---|---|---|---|
| `price` | € 570.105 | € 379.000 | **1,18** | 5,68 |
| `surface_mq` | 95 m² | 80 m² | 0,67 | 3,42 |
| `price_per_mq` | € 5.622 | € 5.073 | **0,47** | 1,83 |

Ci sono due cose da leggere in questa tabella. La prima è che la media supera nettamente la mediana per tutte e tre le variabili, il che indica distribuzioni asimmetriche a destra e porta a una conclusione operativa: la media non è un buon riassunto dell'annuncio milanese tipico, perché una manciata di immobili sopra i dieci milioni di euro la trascina verso l'alto di circa la metà.

La seconda è che il coefficiente di variazione scende da 1,18 a 0,47 non appena si normalizza il prezzo per la superficie. Questo significa che gran parte della variabilità grezza dei prezzi è semplicemente variabilità di dimensione degli immobili. È il primo risultato sostanziale del progetto, ed è anche la ragione per cui `price_per_mq` diventa la variabile di confronto dalla fase 4 in avanti.

### Phase 2 — Probability & Distributions

**Fase completata.** La fase si articola in cinque passaggi, tutti condotti sulle stesse tre variabili centrali.

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

Il salto dal novantesimo al novantanovesimo percentile del prezzo vale quasi due milioni e mezzo di euro. Il dieci per cento più caro del mercato è insomma un mondo a parte, e da solo spiega perché la media rilevata nella fase 1 si collochi a 570.105 euro contro una mediana di 379.000. Sul prezzo al metro quadro la stessa distanza si comprime notevolmente, passando da 8.762 a 15.399 euro, cioè meno del doppio: normalizzare per la superficie toglie di mezzo la dimensione e lascia in gioco soltanto il premio di posizione e di qualità.

**Forma della distribuzione**

| | asimmetria | curtosi (in eccesso) |
|---|---|---|
| `price` | 5,68 | **54,98** |
| `surface_mq` | 3,42 | 19,79 |
| `price_per_mq` | 1,83 | 5,88 |

La curtosi aggiunge un'informazione che l'asimmetria da sola non fornisce. Un valore di 54,98 contro lo zero della distribuzione normale indica code enormemente più pesanti, il che significa che gli eventi estremi non sono affatto rari come una normale con la stessa media e la stessa deviazione standard prevederebbe. La curva normale sovrapposta all'istogramma lo rende evidente a colpo d'occhio: la gaussiana adattata su media e sigma del prezzo risulta troppo larga al centro e troppo sottile in coda. Non sbaglia di poco, sbaglia la forma.

**Trasformazione logaritmica**

Applicando il logaritmo al prezzo, l'asimmetria scende da 5,68 a 0,66 e la curtosi da 54,98 a 1,34. Il risultato non è una distribuzione normale, cosa che nessun dato reale è mai, ma è abbastanza vicino alla simmetria da rendere difendibile l'apparato parametrico impiegato nelle fasi dalla 4 alla 8, e costituisce la giustificazione empirica della specificazione log-log adottata nella fase 7. Sul prezzo al metro quadro il logaritmo funziona addirittura meglio, portando l'asimmetria a −0,07.

Una nota di metodo chiude la fase. Con 16.346 osservazioni, i test formali di normalità come Shapiro-Wilk o D'Agostino rifiutano l'ipotesi nulla su qualunque dataset reale, perché la loro potenza nel rilevare anche una deviazione del tutto irrilevante è di fatto pari a uno. Per questo la fase si appoggia ai Q-Q plot e agli indici di forma anziché ai test, e dichiara esplicitamente il motivo di questa scelta invece di limitarsi a ometterli.

### Phase 3 — Sampling & Confidence Intervals

**Fase completata.** L'impostazione della fase consiste nel trattare i 16.346 annunci puliti come se fossero l'intera popolazione, di cui quindi si conoscono i parametri veri, e nell'estrarne dei campioni. In questo modo la stima ottenuta da ciascun campione e il valore reale sono effettivamente confrontabili, cosa che nella pratica statistica non accade quasi mai. Tutti i calcoli sono condotti su `price_per_mq`.

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

Le due colonne coincidono a meno di pochi euro, e per n = 30 le prime tre cifre sono addirittura identiche. Passando da n = 100 a n = 500 la dispersione si riduce esattamente del fattore radice di cinque previsto dalla teoria, e questo accade su una popolazione con asimmetria 1,83, dove la singola osservazione non è affatto distribuita normalmente. L'istogramma delle medie campionarie risulta invece simmetrico e campanulare già a n = 30: il teorema del limite centrale, qui, si vede all'opera anziché essere semplicemente citato.

Esisterebbe in realtà un termine di confronto più esatto. Poiché i campioni sono estratti senza reinserimento da una popolazione finita, la formula corretta sarebbe sigma diviso radice di n, moltiplicato per il fattore di correzione per popolazione finita, che a n = 500 porterebbe il valore teorico da 118,26 a 116,40 euro. La correzione risulta però trascurabile, perché n resta piccolo rispetto a una popolazione di 16.346 unità, e il confronto viene lasciato sulla formula standard perché è quella di cui la fase intende discutere.

**Copertura degli intervalli**

| n | copertura osservata |
|---|---|
| 30 | **94,2%** |
| 100 | **93,8%** |
| 500 | **94,5%** |

Tutte e tre le coperture si collocano sotto il 95% nominale, ma leggere correttamente questa tabella richiede di sapere quanto vale il suo margine d'errore. Ogni copertura è essa stessa una stima, ricavata da mille ripetizioni, e il suo errore Monte Carlo vale circa sette decimi di punto. Le tre cifre risultano quindi compatibili sia fra loro sia con il 95%, il che significa che da questa singola esecuzione non si può concludere granché, e men che meno che n = 100 copra peggio di n = 30, che è quello che la tabella sembrerebbe suggerire.

L'andamento vero si vede solo ripetendo l'intero esperimento. Su **sei serie indipendenti** da 1.000 intervalli ciascuna la copertura media risulta:

| n | media di 6 serie | intervallo osservato |
|---|---|---|
| 30 | **93,53%** | 93,0 – 93,9 |
| 100 | 94,50% | 93,8 – 95,9 |
| 500 | 95,17% | 94,5 – 96,2 |

Con sei serie il quadro diventa leggibile. A n = 30 tutte e sei cadono fra 93,0 e 93,9 senza mai avvicinarsi al 95%, il che indica una sotto-copertura sistematica; la deviazione standard fra le serie, pari a 0,35 punti, è troppo piccola perché si possa trattare di rumore. A n = 500, invece, la media risale a 95,17%, cioè esattamente al valore nominale. Serve dunque un ordine di grandezza in più di ripetizioni perché emerga dal rumore ciò che una sola tabella non può mostrare. La spiegazione del fenomeno è quella attesa: l'intervallo costruito sulla distribuzione t assume una popolazione normale, mentre qui l'asimmetria vale 1,83 e a n = 30 il teorema del limite centrale non ha ancora finito il suo lavoro, cosicché l'intervallo mantiene meno di quanto promette. Resta però una spiegazione che la singola tabella iniziale non basta a dimostrare.

Questo è il risultato metodologico della fase, e vale più di una tabella di coperture ordinate: il livello di confidenza è una proprietà della procedura sotto le sue assunzioni, e misurarla richiede a sua volta abbastanza dati per distinguere il segnale dal rumore. Portare le ripetizioni da mille a diecimila ridurrebbe il margine d'errore a due decimi di punto e renderebbe la tabella leggibile per quello che sembra dire.

Una nota sulla riproducibilità. Le funzioni `draw_sample` e `confidence_intervals` costruiscono ciascuna un generatore `np.random.default_rng(42)` e lo passano a ogni chiamata di `.sample(...)`, così che due esecuzioni consecutive producano un output identico riga per riga, cosa verificata. È essenziale che il generatore venga creato una volta sola fuori dal ciclo e lasciato avanzare: passare `random_state=42` direttamente a `.sample()` produrrebbe mille copie dello stesso campione, non mille campioni riproducibili.

### Phase 4 — Hypothesis Testing

**Fase completata.** La fase conduce quattro confronti formali fra due campioni su `price_per_mq`, tutti bilaterali e con livello di significatività fissato a 0,05.

Tutto l'apparato del test è raccolto in un'unica funzione riusabile, `two_sample_test(group_1, group_2)`, che restituisce il test di Levene, il t-test di Welch, i gradi di libertà, l'intervallo di confidenza al 95% per la differenza fra le medie e la d di Cohen. La funzione `hypothesis_testing` si limita a estrarre i gruppi e a chiamarla quattro volte, cosicché la logica statistica viene scritta e verificata una volta sola mentre i confronti restano dei semplici dati. I gradi di libertà di Welch–Satterthwaite e l'intervallo di confidenza sono calcolati esplicitamente a partire dalla formula anziché letti da un output già pronto, perché in questa fase costruire il test a mano è precisamente il punto dell'esercizio.

**Test 1 — due zone.**

> **H₀**: μ(zona A) = μ(zona B) — il prezzo medio al m² è uguale nelle due zone
> **H₁**: μ(zona A) ≠ μ(zona B) — bilaterale

Le due coppie sono state scelte apposta per contrasto. La prima mette a confronto zone lontanissime fra loro, dove l'esito del test è scontato e la quantità davvero interessante è la dimensione dell'effetto. La seconda confronta invece `Ripamonti, Vigentino` con `Porta Vittoria, Lodi`, due zone i cui centri distano 2,4 chilometri e che hanno numerosità quasi identiche: è qui che il test svolge un lavoro vero.

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

Le due colonne portano formalmente alla stessa conclusione, cioè il rifiuto dell'ipotesi nulla, ma non significano niente di simile.

Nella colonna di sinistra la d di Cohen vale 2,84, il che significa che le due distribuzioni sono separate da quasi tre deviazioni standard. In una situazione del genere il p-value è un numero privo di contenuto informativo, e la quantità che conta davvero è l'intervallo di confidenza, che colloca il divario fra 8.081 e 8.941 euro al metro quadro.

Nella colonna di destra sta invece il risultato didattico della fase. Il p-value di 0,024 porta a rifiutare l'ipotesi nulla al livello del 5%, ma la d di Cohen vale −0,14, che secondo le convenzioni dello stesso Cohen è un effetto trascurabile, dato che la soglia per definirlo anche solo piccolo è 0,2. Soprattutto, l'intervallo di confidenza va da −393 a −28 euro al metro quadro, il che colloca il suo estremo superiore a soli 28 euro dallo zero. Tradotto su un appartamento di 80 metri quadri, il divario vero fra le due zone potrebbe valere 31.000 euro come 2.200: il test ha stabilito che le due zone non sono identiche, e nient'altro. È esattamente per questo che la dimensione dell'effetto e l'intervallo di confidenza compaiono accanto a ogni p-value, e non si tratta di un avvertimento astratto: con circa 500 osservazioni per gruppo, una differenza del quattro per cento basta a superare la soglia di significatività.

**Test 2 — una caratteristica dell'immobile.** Lo stesso apparato viene poi applicato a `elevator` e a `condition`, per mostrare che la verifica d'ipotesi non riguarda soltanto la geografia.

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

Entrambi gli effetti risultano nettamente significativi e di dimensione media, con d pari a 0,43 e a −0,37, cioè un ordine di grandezza sopra quello della coppia di zone ravvicinate. Si tratta però di differenze grezze, calcolate senza alcun controllo: l'ascensore è più frequente negli edifici recenti e centrali, e gli immobili da ristrutturare sono sistematicamente più grandi e più vecchi. Quanto di quei 1.121 euro al metro quadro appartenga davvero all'ascensore, e non alla zona o al tipo di edificio in cui l'ascensore si trova, è una domanda che il t-test non può nemmeno porsi. Serve la regressione multipla della fase 8, dove le stesse variabili rientrano controllate per zona e superficie, e il confronto fra il coefficiente stimato lì e la differenza grezza riportata qui è uno dei risultati previsti della fase 9.

Vale la pena spiegare la scelta fra Levene e Welch. Il test di Levene rifiuta l'omogeneità delle varianze in tre casi su quattro, e lo fa in modo clamoroso nel confronto fra `Centro` e periferia, dove le deviazioni standard valgono 4.206 contro 1.009 e le due zone non hanno in comune nemmeno l'ordine di grandezza della dispersione. Soltanto per la coppia di zone ravvicinate il test non rifiuta, con p pari a 0,324.

Nonostante questo, il test di Welch viene usato in tutti e quattro i confronti. La ragione è semplice: quando le varianze sono davvero omogenee Welch coincide in pratica con Student, come si vede dal fatto che nella coppia ravvicinata i gradi di libertà scendono a 1.023,4 contro i 1.027 di Student, una differenza irrilevante; quando invece non lo sono, Student sbaglia. Un test che non costa nulla nel caso favorevole e che salva la situazione in quello sfavorevole non ha bisogno di essere scelto caso per caso. Si noti per contrasto il crollo dei gradi di libertà nel primo confronto, dove si passa a 428,8 contro gli 813 di Student: è Welch che sconta la varianza sproporzionata del `Centro`.

La fase discute infine l'errore di primo tipo, cioè il rifiuto di un'ipotesi nulla vera, che corrisponde al cinque per cento di casi che si accettano fissando il livello di significatività; l'errore di secondo tipo; e il motivo per cui una numerosità elevata rende statisticamente significative differenze minuscole e prive di rilevanza pratica. Quest'ultimo punto, in questa fase, non è un'ipotesi teorica ma un risultato misurato, ed è la colonna di destra della prima tabella.

### Phase 5 — ANOVA

**Fase completata.** L'ANOVA è l'estensione naturale della fase 4 a tutte e 32 le macrozone considerate insieme, e viene condotta su 16.334 annunci, dato che i 12 privi del campo `macrozone` si autoescludono. La fase è composta da cinque funzioni orchestrate da `anova_phase`: `anova_analysis`, `welch_anova`, `residual_diagnostics`, `tukey_posthoc` e `plot_macrozone_boxplots`.

> **H₀**: μ₁ = μ₂ = … = μ₃₂ — il prezzo medio al m² è uguale in ogni zona di Milano
> **H₁**: almeno una zona differisce

**ANOVA a una via** (`anova_analysis`)

| | |
|---|---|
| F | **658,07** |
| gradi di libertà | 31; 16.302 |
| p | < 10⁻³⁰⁰ (restituito come 0.0) |
| η² | **0,556** |

L'ipotesi nulla viene respinta senza margine di discussione, ma anche in questo caso il p-value è la parte meno interessante del risultato: con oltre sedicimila osservazioni e un rapporto di 3,6 volte fra la zona più cara e la più economica, nessun altro esito era concepibile. La quantità che porta informazione è l'eta quadro, pari a 0,556, il che significa che la sola appartenenza a una macrozona spiega il 55,6% della varianza del prezzo al metro quadro. Più della metà di ciò che distingue un annuncio da un altro, una volta tolta di mezzo la superficie, è dunque geografia: è il numero che giustifica tanto le dummy di zona della fase 8 quanto l'intero deliverable della fase 10. Anche l'eta quadro è calcolato a mano, come rapporto fra la devianza tra i gruppi e quella totale, anziché ripreso da un output già pronto.

**Verifica delle assunzioni** (`welch_anova`, `residual_diagnostics`)

Il test di Levene restituisce una statistica di 89,40 con p praticamente nullo, il che indica che l'omogeneità delle varianze è violata in modo grossolano. Del resto lo lasciavano già prevedere le deviazioni standard calcolate per zona, che vanno dagli 826 euro di Forlanini ai 4.206 del Centro, un fattore cinque. Da qui la scelta di affiancare l'ANOVA di Welch, che non assume l'omogeneità: restituisce F = 451,70 con gradi di libertà pari a 31 e 4.249,0 e p ancora praticamente nullo. Le due statistiche F non sono confrontabili fra loro come numeri, perché Welch penalizza pesantemente i gradi di libertà del denominatore portandoli da 16.302 a 4.249, ma la conclusione non si sposta di un millimetro. È il caso in cui conviene dichiarare che l'assunzione è violata e che il risultato regge comunque, invece di dover scegliere fra le due affermazioni.

Il grafico `charts/anova_residuals.png` mostra il fenomeno in forma visiva. Poiché i valori stimati sono soltanto 32, cioè le medie di gruppo, i residui si dispongono in 32 strisce verticali, e queste strisce si allargano progressivamente da sinistra a destra: attorno ai 4.000 euro al metro quadro i residui restano entro cinquemila euro, mentre attorno ai 12.000 sfiorano i quindicimila. Le zone care, in altre parole, non sono soltanto più care ma anche internamente più disomogenee. Il Q-Q plot dei residui conferma poi la coda destra pesante già nota dalla fase 2, il che significa che anche la normalità dei residui è violata; con 16.334 osservazioni, però, il teorema del limite centrale rende questa seconda violazione di scarsa conseguenza per il test F, a differenza dell'eteroschedasticità.

**Post-hoc: Tukey HSD** (`tukey_posthoc`)

Sulle 496 coppie possibili, 426 risultano significative, cioè l'86%, e 70 no. La correzione per confronti multipli è in questo caso obbligatoria: 496 t-test indipendenti condotti al livello del 5% produrrebbero per costruzione circa 25 falsi positivi, un numero pari a più di un terzo delle 70 coppie che qui restano non significative.

L'effetto della correzione si vede meglio su un caso già noto — **la coppia ravvicinata della fase 4**:

| | fase 4 (Welch, non corretto) | fase 5 (Tukey, corretto) |
|---|---|---|
| `Ripamonti, Vigentino` vs `Porta Vittoria, Lodi` | p = **0,024** → rifiuto | p-adj = **0,992** → non rifiuto |

La differenza è la stessa, 211 euro al metro quadro, i dati sono gli stessi, e la conclusione è opposta. Nella fase 4 quel confronto era l'unico posto in cui si stava guardando, mentre qui è uno dei 496 possibili, e il livello di confidenza viene ricalibrato di conseguenza: l'intervallo di Tukey si allarga fino a [−626; +205] e finisce per includere lo zero. Non è che uno dei due test sbagli, semplicemente rispondono a due domande diverse, e la distanza fra queste due domande è precisamente il problema dei confronti multipli.

Le coppie con lo scarto più ampio sono tutte confronti fra il `Centro`, oppure `Bisceglie, Baggio, Olmi`, e il resto della città; la massima è proprio quella fra queste due zone, con 8.511 euro al metro quadro di differenza, la stessa già misurata nella fase 4. All'estremo opposto, la più piccola differenza che sopravvive alla correzione vale 360 euro al metro quadro e riguarda `Famagosta, Barona` contro `Uptown, Cascina Merlata, Viale Certosa`, con p corretto pari a 0,027. Sotto quella soglia, con queste numerosità, il test di Tukey non distingue più.

**Box plot per macrozona** (`plot_macrozone_boxplots`). Il grafico `charts/macrozone_boxplots.png` dispone le 32 zone in ordine di mediana crescente. È la controparte visiva del test, e mostra tre cose che la statistica F non dice.

La prima è che la salita è continua: dalla mediana di 3.216 euro di `Bisceglie, Baggio, Olmi` fino agli 11.481 del `Centro` non compare nessun salto, nessuna soglia che separi un centro da una periferia. Sul prezzo al metro quadro, Milano è un gradiente e non due mercati distinti.

La seconda è che la prima dozzina di zone forma comunque un plateau: da `Bisceglie` fino a `Udine, Lambrate` le mediane stanno tutte fra 3.200 e 4.500 euro, cioè dodici zone diverse comprese in appena 1.300 euro, mentre le ultime quattro ne coprono da sole quasi duemila. È questa la ragione per cui le 70 coppie non significative del test di Tukey si concentrano quasi tutte in fondo alla classifica: lì le zone sono davvero vicine fra loro.

La terza è che l'ampiezza delle scatole cresce insieme alla mediana: lo scarto interquartile di `Bisceglie` sta dentro il migliaio di euro, mentre quello del `Centro` supera i cinquemila. Si tratta della stessa eteroschedasticità già vista nel grafico dei residui, osservata però da un'altra angolazione, e ha una lettura concreta: comprare in centro non significa soltanto pagare di più, ma anche entrare in un mercato molto meno prevedibile.

### Phase 6 — Correlation

**Fase completata.** La fase misura le relazioni bivariate con `price`, e lo fa calcolando ciascuna relazione due volte, con Pearson e con Spearman. Le funzioni sono quattro, raccolte sotto `correlation_phase`: `prepare_correlation_data` codifica `condition` su una scala ordinale da 1 a 4, `correlation_analysis` calcola i due coefficienti con i rispettivi p-value, `correlation_matrix` produce una heatmap su tutte le coppie di variabili e `pearson_spearman_comparison` un grafico a barre affiancate.

| variabile | Pearson | Spearman | scarto | n |
|---|---|---|---|---|
| `surface_mq` | **0,789** | 0,763 | −0,026 | 16.346 |
| `bathrooms` | 0,623 | 0,646 | +0,023 | 15.502 |
| `rooms` | 0,547 | **0,646** | **+0,100** | 16.240 |
| `floor` | 0,136 | 0,167 | +0,031 | 15.802 |
| `condition_numeric` | **0,051** | 0,115 | +0,064 | 15.759 |

Tutti i coefficienti risultano significativi, con p inferiore a 10⁻¹⁰, e per le prime tre variabili il p-value va addirittura in underflow e viene stampato come zero. Ma con circa sedicimila osservazioni la significatività non distingue nulla, esattamente come già accadeva nella fase 4. Quello che distingue è la magnitudine dei coefficienti, e soprattutto lo scarto fra le due colonne.

**Dove Pearson e Spearman divergono, e perché**

Il caso più interessante è quello di `rooms`, dove i due coefficienti valgono 0,547 e 0,646, con dieci punti di differenza. La causa sta nel dato e non nella statistica: la variabile è troncata in alto, perché il valore `5+` della sorgente è stato mappato a 5, cosicché un attico da dieci locali e un quadrilocale grande finiscono per condividere lo stesso valore. Pearson, che lavora sui valori, viene penalizzato tanto da questo tetto artificiale quanto dalle code del prezzo, mentre Spearman, che lavora sui ranghi, ne risente molto meno. La relazione vera fra numero di locali e prezzo è quindi più forte di quanto Pearson dichiari, e l'unico modo di accorgersene è calcolarli entrambi.

La superficie va invece nella direzione opposta, con 0,789 contro 0,763, ed è l'unico caso in cui Pearson supera Spearman. La relazione fra prezzo e superficie è infatti genuinamente quasi lineare sui valori, e i grandi immobili di lusso, che si collocano in coda su entrambe le variabili, rafforzano Pearson mentre in una graduatoria conterebbero quanto qualsiasi altra osservazione. È la conferma bivariata di ciò che la fase 7 andrà a modellare.

Il risultato negativo della fase riguarda `condition`, ed è più informativo di molti risultati positivi: il coefficiente di Pearson vale 0,051, cioè una correlazione praticamente nulla fra stato di conservazione e prezzo. Questo non significa che ristrutturare non paghi, ma che la scala ordinale da 1 a 4 non cattura la relazione. Nel dataset, infatti, gli immobili `Da ristrutturare` sono sistematicamente più grandi, con una media di 107,6 metri quadri contro i 90,9 di quelli in stato `Ottimo / Ristrutturato`, e sono concentrati nei quartieri storici: la penalizzazione dovuta allo stato e il premio dovuto a dimensione e posizione si elidono a vicenda, e sul prezzo totale non resta quasi nulla. La fase 4, che confrontava le stesse due categorie sul prezzo al metro quadro anziché sul prezzo assoluto, aveva invece trovato una differenza netta di 984 euro al metro quadro con d pari a −0,37. Stessa variabile, due misure diverse, due risposte opposte: è un caso da manuale del perché la variabile dipendente vada scelta prima di interpretare il coefficiente.

**Multicollinearità, in anticipo sulla fase 8**

La heatmap in `charts/correlation_matrix.png` copre tutte le coppie di variabili, ma il blocco che conta davvero non è la riga del prezzo, bensì il triangolo delle correlazioni fra i predittori.

| | `surface_mq` | `rooms` | `bathrooms` |
|---|---|---|---|
| `surface_mq` | 1 | **0,751** | **0,726** |
| `rooms` | 0,751 | 1 | **0,710** |
| `bathrooms` | 0,726 | 0,710 | 1 |

Tre variabili correlate fra loro fra 0,71 e 0,75 stanno misurando in gran parte la stessa cosa, cioè quanto è grande l'immobile. È il problema di multicollinearità della fase 8 che diventa visibile per la prima volta, ed è il motivo per cui quella fase calcola i VIF anziché infilare tutte e tre le variabili nel modello e fidarsi. Merita attenzione anche il fatto che `rooms` correli con `surface_mq` a 0,751, cioè più fortemente di quanto correli con `price`, dove si ferma a 0,547: il numero di locali dice di più sulla metratura che sul prezzo.

Le variabili `condition_numeric` e `floor` sono invece scorrelate da tutto il resto, con correlazioni in valore assoluto non superiori a 0,14, il che le rende innocue nel modello multiplo: non spiegano molto, ma non disturbano nessun altro predittore.

I grafici della fase sono due. Il primo, `charts/correlation_matrix.png`, è una heatmap annotata con palette divergente centrata sullo zero, scelta in modo che il blocco caldo dei predittori dimensionali si stacchi a colpo d'occhio dalla fascia neutra di `condition` e `floor`. Il secondo, `charts/pearson_spearman_comparison.png`, affianca per ciascuna variabile le barre delle due misure: il divario di `rooms` è di gran lunga il più evidente, ed è anche il grafico che rende visibile come `rooms` e `bathrooms`, pur distanti secondo Pearson, arrivino alla stessa identica correlazione di rango di 0,646.

Che la correlazione non implichi causalità è un principio che qui trova un esempio concreto anziché uno slogan. La variabile `bathrooms` correla con il prezzo a 0,62, ma aggiungere un secondo bagno a un appartamento a Quarto Oggiaro non lo avvicina certo a Brera. Il numero di bagni è semplicemente un indicatore della presenza di immobili grandi, centrali e costosi, e non a caso correla con la superficie a 0,726, quasi quanto correla con il prezzo. Il fattore confondente è la dimensione e, soprattutto, la posizione, che la fase 5 ha appena stabilito spiegare da sola il 55,6% della varianza del prezzo al metro quadro. È esattamente per questo che la fase 8 introduce il controllo per la zona.

### Phase 7 — Linear Regression

**Fase completata.** La fase stima due specificazioni diverse su tutti i 16.346 annunci. Le variabili `price` e `surface_mq` sono complete, e il filtro di positività richiesto dal logaritmo non scarta nulla, dato che i valori minimi sono 20.240 euro e 15 metri quadri. Le funzioni sono sette, raccolte sotto `linear_regression_phase`: tre per il modello semplice e tre per il log-log, ciascuna terna composta da stima, diagnostica dei residui e test di Breusch-Pagan.

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

Ogni metro quadro aggiuntivo si porta dietro 8.274 euro di prezzo, e la superficie da sola spiega il 62,2% della varianza. Il coefficiente va però letto per quello che è: il metro quadro marginale costa 8.274 euro, mentre il metro quadro medio del dataset ne costa 5.622, come rilevato nella fase 1. Non si tratta di una contraddizione ma della stessa cosa detta due volte, e cioè che il prezzo al metro quadro cresce con la dimensione dell'immobile; la specificazione log-log discussa più avanti lo quantifica con precisione.

L'intercetta, pari a −215.563 euro, non ha invece alcuna interpretazione sensata, perché corrisponde al prezzo che il modello attribuirebbe a un immobile di zero metri quadri. Il minimo osservato è di 15 metri quadri, quindi lo zero si trova lontano da qualunque dato reale e l'intercetta è soltanto il punto in cui la retta incrocia un asse che non descrive nessun immobile esistente. È il classico coefficiente che si riporta senza interpretarlo.

**La diagnostica boccia il modello** (`linear_residual_diagnostics`, `breusch_pagan_test`)

Il test di Breusch-Pagan restituisce una statistica LM di 2.743,0 con p praticamente nullo, e il grafico `charts/linear_regression_residuals.png` ne mostra il motivo nella forma più didattica possibile. I residui si aprono a ventaglio in modo perfetto: attorno a valori stimati di 200.000 euro restano entro poche decine di migliaia di euro, mentre oltre i quattro milioni arrivano a sei milioni in entrambe le direzioni. La varianza dell'errore non è dunque costante, e l'assunzione di omoschedasticità su cui poggia l'OLS è violata in modo plateale. Il Q-Q plot dei residui aggiunge una seconda violazione, con la classica forma a S che segnala code molto più pesanti di quelle di una normale.

Le conseguenze sono precise e vale la pena esplicitarle. Il coefficiente β₁ = 8.274 resta corretto, perché l'eteroschedasticità non distorce la stima puntuale dell'OLS, ma il suo errore standard no: di conseguenza l'intervallo di confidenza [8.175; 8.373] e la statistica t pari a 164 sono inaffidabili. È precisamente il motivo per cui la fase 8 ricorrerà a errori standard robusti di tipo HC3.

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

In questa specificazione β₁ è un'elasticità, il che significa che a un aumento dell'1% della superficie corrisponde un aumento dell'1,09% del prezzo. Il valore interessante non è però 1,09 in sé, bensì il suo confronto con l'unità: se il prezzo fosse proporzionale alla superficie, cioè se il prezzo al metro quadro fosse indipendente dalla dimensione, l'elasticità varrebbe esattamente 1. L'intervallo di confidenza, che va da 1,0786 a 1,1041, esclude l'unità con ampio margine. A Milano gli immobili grandi costano dunque più che proporzionalmente, e raddoppiare la superficie fa più che raddoppiare il prezzo. È il risultato principale della fase, e coincide con il fatto che la specificazione lineare esprimeva goffamente attraverso un'intercetta negativa.

**Perché il log-log è preferito, e perché non per l'R²**

I due valori di R², 0,622 e 0,633, non sono confrontabili fra loro, perché misurano la varianza spiegata di due variabili dipendenti diverse, `price` nel primo caso e `log(price)` nel secondo. Metterli in classifica sarebbe un errore, ed è per questo che la preferenza per una delle due specificazioni non si argomenta su quel terreno.

La preferenza si argomenta invece sui residui. Il test di Breusch-Pagan rifiuta ancora, con p pari a 5 × 10⁻⁴¹, il che significa che la specificazione log-log non risolve l'eteroschedasticità ma la riduce. La statistica LM scende però da 2.743 a 180, cioè di un fattore quindici, e con 16.346 osservazioni il test rifiuterebbe comunque qualsiasi deviazione anche minima, come si era già visto a proposito dei test di normalità nella fase 2. È quindi il confronto fra le due magnitudini a portare informazione, non l'esito del test.

Il grafico chiude poi la questione senza bisogno di ulteriori statistiche. In `charts/log_linear_regression_residuals.png` il ventaglio è scomparso, la nuvola dei residui presenta un'ampiezza pressoché costante su tutto l'intervallo dei valori stimati, e il Q-Q plot resta sulla diagonale quasi ovunque, con un lieve scostamento nella sola coda inferiore. Confrontato con la S marcata del modello lineare, si tratta di un'altra categoria di aderenza alle assunzioni.

La seconda specificazione è quindi quella preferita, ed è anche l'unica direttamente confrontabile con il modello completo della fase 8, che parte proprio da qui e vi aggiunge altri regressori.

**Grafico della retta.** Il file `charts/linear_regression.png` riporta la nuvola dei 16.346 punti con la retta OLS sovrapposta, in scala originale. Il ventaglio dei residui si intravede già qui, prima ancora di andare a guardare il grafico dedicato.

### Phase 8 — Multiple Linear Regression

```
log(Price) = β₀ + β₁·log(Surface) + β₂·Rooms + β₃·Bathrooms + β₄·Condition
           + β₅·Elevator + β₆·Floor + β₇·Heating + β₈·Luxury + dummy di zona + ε
```

**Fase completata.** Il modello è scritto in forma di formula tramite `sm.formula.ols`, cosicché le espressioni `C(macrozone)` e `C(heating)` generano da sole le rispettive variabili dummy: 31 per le macrozone e 2 per il riscaldamento, assumendo come riferimento la prima categoria in ordine alfabetico. La fase è composta da sette funzioni raccolte sotto `multiple_regression_phase`.

**Il campione si restringe.** Poiché la regressione richiede tutte le variabili contemporaneamente, l'eliminazione delle righe incomplete costa 1.707 osservazioni, portando il campione da 16.346 a 14.639 righe, cioè il 10,4% in meno. È il prezzo cumulato dei valori mancanti sparsi su `bathrooms`, `condition` e `floor`, rispettivamente al 5,2%, 3,6% e 3,3%: la stima annunciata nella sezione sulla pulizia trova qui la sua misura effettiva. Tutti i numeri di questa fase valgono su quelle 14.639 righe, comprese le due specificazioni della tabella di confronto finale, che sono state rifittate sullo stesso sottoinsieme proprio perché AIC e R² risultino confrontabili.

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

La correlazione fra i tre predittori dimensionali osservata nella fase 6, compresa fra 0,71 e 0,75, si traduce in VIF di 4,67 e 4,17: valori alti, vicini alla soglia convenzionale di 5, ma comunque al di sotto di essa. Nessuna variabile viene quindi eliminata, e la tabella serve a documentare una decisione presa sulla base dei numeri anziché a giustificarne una già presa in partenza. Vale la pena essere espliciti sul significato di questi valori: un VIF di 4,67 indica che l'errore standard di `log_surface` è circa 2,2 volte quello che si avrebbe con predittori scorrelati. La collinearità, insomma, non è assente: è tollerata consapevolmente.

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

I due valori di R² distano appena tre decimillesimi nonostante il modello impieghi circa quaranta regressori. Con 14.639 osservazioni la penalizzazione introdotta dall'aggiustamento è minima, e il confronto serve appunto a mostrare che in questo caso il rischio di sovradattamento non si materializza; con lo stesso numero di regressori e poche centinaia di osservazioni sarebbe andata diversamente.

Trattandosi di una variabile dipendente logaritmica, i coefficienti si leggono come variazioni percentuali approssimate. Un bagno in più è associato a un prezzo superiore dell'8,9%, l'ascensore del 7,9%, un gradino nella scala di `condition` dell'8,1% e un piano più in alto dell'1,2%. Per il flag `luxury` l'approssimazione lineare non basta più e occorre la conversione esatta, che dà un premio del 44%.

Merita attenzione il fatto che l'elasticità della superficie scenda da 1,09 a 0,80. Nella fase 7 `log_surface` era l'unico regressore e assorbiva quindi tutto ciò che correla con la dimensione dell'immobile, mentre qui `bathrooms` e `rooms` fanno parte del modello e se ne prendono una porzione. È lo stesso fenomeno già osservato nella fase 6, visto però dall'altro lato, ed è il motivo per cui il coefficiente di una regressione semplice e quello di una multipla non sono la stessa quantità: rispondono a domande diverse.

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

L'R² aggiustato passa da 0,8458 senza le dummy di zona a 0,9059 con esse: le sole dummy di macrozona aggiungono quindi sei punti di varianza spiegata a un modello che ne spiegava già l'85%.

Nel passaggio due predittori perdono la significatività, ed è il risultato più istruttivo della fase.

- **`rooms`** passa da p = 0,006 a p = 0,593. A parità di superficie, il numero di locali sembrava dire qualcosa sul prezzo; una volta noto il quartiere non dice più niente. Stava funzionando da indicatore di localizzazione — appartamenti tagliati in molte stanze piccole sono tipici di certe zone — non da caratteristica con un valore proprio.
- **`heating` centralizzato** passa da p = 0,012 a p = 0,387, per la stessa ragione: il riscaldamento centralizzato è una caratteristica dei condomini di certe epoche e certi quartieri.

Altri due coefficienti si ridimensionano senza perdere significatività: `luxury` quasi si dimezza, passando da 0,679 a 0,364, ed `elevator` cala di circa un terzo, da 0,120 a 0,079. Metà del premio associato al lusso era, letteralmente, il quartiere.

Un coefficiente si muove infine nella direzione opposta: `floor` quadruplica, passando da 0,0027 a 0,0121, e il suo p-value scende da 0,008 a meno di 0,001. Senza il controllo per la zona l'effetto del piano risultava mascherato, perché i palazzi alti si trovano tanto nei quartieri più cari quanto nelle periferie di edilizia popolare e i due gruppi si annullavano a vicenda. È il caso in cui l'introduzione di un controllo non riduce un effetto ma lo rivela.

**Errori standard robusti** (`robust_standard_errors`)

Lo stesso modello viene rifittato con `cov_type='HC3'`. Gli errori standard salgono, come era atteso dopo il test di Breusch-Pagan della fase 7: per `log_surface` passano da 0,0072 a 0,0091, con un aumento del 26%, e per l'intercetta da 0,0285 a 0,0385, con un aumento del 35%. Le variabili dotate di coefficienti forti non si spostano di una virgola nelle conclusioni, mentre le due categorie di `heating`, già non significative, lo diventano ancora di più, con il p-value che passa da 0,779 a 0,841. Nessuna conclusione della fase dipende quindi dalla scelta fra errori standard classici e robusti, ed è esattamente questa l'informazione che l'analisi doveva produrre: non che gli HC3 siano migliori in astratto, ma che in questo caso non cambiano la risposta.

**Residui** (`multiple_residual_diagnostics`) — `charts/multiple_regression_residuals.png`

La nuvola dei residui contro i valori stimati presenta un'ampiezza sostanzialmente costante da un log-prezzo di 12 fino a 15, senza alcuna traccia del ventaglio osservato nella fase 7. Il Q-Q plot resta sulla diagonale per tutta la parte centrale, con uno scostamento nella coda sinistra che corrisponde a un gruppo di immobili nettamente sopravvalutati dal modello, cioè annunci molto più economici di quanto le loro caratteristiche e la loro zona facciano prevedere. Si tratta di poche decine di casi su 14.639, che non minacciano le stime, ma costituiscono l'unico residuo di struttura non spiegata rimasto.

**Confronto fra modelli** (`model_comparison`)

| modello | R² adjusted | AIC |
|---|---|---|
| log-log semplice | 0,6554 | 14.531,0 |
| multiplo completo | **0,9059** | **−4.441,2** |

Entrambi i modelli sono stimati sulle stesse 14.639 righe e sulla stessa variabile dipendente `log_price`, che è la condizione necessaria perché il confronto abbia senso. È anche il motivo per cui il modello lineare della fase 7 non compare in tabella: la sua variabile dipendente è `price`, e un AIC calcolato su una scala diversa non sarebbe confrontabile. Il salto è netto su entrambi i criteri, dato che la varianza spiegata passa dal 66% al 91% e i circa diciannovemila punti di AIC in meno indicano che l'aggiunta dei regressori paga ampiamente il costo della maggiore complessità.

**Una promessa che i dati non consentono di mantenere.** Le versioni precedenti di questo README prevedevano un'analisi di sensibilità su `elevator`, da condurre rifittando il modello sul sottoinsieme delle 13.572 righe con il campo effettivamente compilato. Quel test non è però eseguibile: nella sorgente la variabile vale `1.0` oppure `NaN` e mai `0`, quindi il sottoinsieme con il campo compilato contiene esclusivamente immobili dotati di ascensore. In assenza di variazione il coefficiente non è identificabile e la variabile verrebbe semplicemente scartata dalla stima. Il ragionamento sulla codifica resta valido, perché l'errore di classificazione può solo attenuare β verso lo zero e quindi 0,0789 è semmai una sottostima, ma si tratta di un'argomentazione e non di una verifica empirica, e viene qui dichiarata come tale.

### Phase 9 — Statistical Conclusions

**Fase completata.** La fase non produce alcuna nuova stima: riusa il modello già stimato nella fase 8, che `multiple_regression_phase` restituisce insieme al frame dei dati, e ne ricava la tabella su cui vengono scritte le conclusioni. Le funzioni sono tre: `conclusions_table` costruisce coefficienti, intervalli di confidenza al 95%, p-value e flag di significatività; la partizione fra predittori significativi e non significativi avviene dentro `conclusions_phase`; e `zone_variance_share` quantifica il contributo della zona.

**I predittori, con il loro intervallo di confidenza**

| predittore | β | IC 95% | significativo a α = 0,05 |
|---|---|---|---|
| `log_surface` | **0,8019** | [0,7878; 0,8160] | ✅ |
| `luxury` | **0,3642** | [0,3526; 0,3757] | ✅ |
| `bathrooms` | 0,0893 | [0,0806; 0,0980] | ✅ |
| `condition_numeric` | 0,0811 | [0,0769; 0,0853] | ✅ |
| `elevator` | 0,0789 | [0,0699; 0,0878] | ✅ |
| `floor` | 0,0121 | [0,0105; 0,0137] | ✅ |
| `rooms` | −0,0018 | [−0,0086; 0,0049] | ❌ |
| `heating` autonomo | −0,0035 | [−0,0283; 0,0212] | ❌ |
| `heating` centralizzato | −0,0108 | [−0,0353; 0,0137] | ❌ |

Sei predittori su nove risultano significativi. Il modo in cui questa fase riporta i risultati passa però dagli intervalli di confidenza e non dai p-value, perché l'intervallo dice quanto vale l'effetto e con quale precisione, mentre il p-value si limita a dire se l'effetto è distinguibile da zero. È la stessa distinzione su cui la fase 4 aveva già insistito discutendo la coppia di zone ravvicinate.

**Le conclusioni, nella forma in cui vanno scritte**

> La **superficie** presenta una relazione positiva e statisticamente significativa con il prezzo (β = 0,802, IC 95% [0,788; 0,816], p < 0,001). Dopo aver controllato per le altre caratteristiche dell'immobile **e per la zona**, resta di gran lunga il predittore più forte: un aumento dell'1% della superficie è associato a un aumento dello **0,80%** del prezzo, a parità di tutto il resto.

> Il flag **lusso** è associato a un prezzo superiore del **44%** (β = 0,364, IC 95% [0,353; 0,376], p < 0,001) rispetto a un immobile con le stesse caratteristiche e nella stessa zona. Senza controllo di zona lo stesso coefficiente valeva 0,679, cioè un premio del 97%: **più della metà di quello che sembra un premio di lusso è in realtà il quartiere**.

> Un **bagno** aggiuntivo è associato a un prezzo superiore del **9,3%** (β = 0,089, IC 95% [0,081; 0,098], p < 0,001), un gradino nella scala dello **stato di conservazione** all'**8,4%** (β = 0,081, IC 95% [0,077; 0,085]), la presenza dell'**ascensore** all'**8,2%** (β = 0,079, IC 95% [0,070; 0,088]) e ogni **piano** di altezza all'**1,2%** (β = 0,012, IC 95% [0,011; 0,014]). Le percentuali sono e^β − 1; per la superficie, che entra in logaritmo, β è direttamente un'elasticità e la conversione non si applica.

> Il **numero di locali** non presenta un'associazione significativa con il prezzo una volta controllate superficie, bagni e zona (β = −0,002, IC 95% [−0,009; 0,005], p = 0,593). Lo stesso vale per il **tipo di riscaldamento** (p = 0,779 e p = 0,387). Nel caso dei locali la conclusione è più forte di un semplice "non significativo": l'intervallo di confidenza colloca l'effetto vero fra **−0,9% e +0,5%**, cioè lo esclude in entrambe le direzioni. Non è ignoranza sull'effetto, è la constatazione che è trascurabile.

**Quanto pesa la posizione** (`zone_variance_share`)

| | R² adjusted |
|---|---|
| modello senza dummy di zona | 0,8458 |
| modello con dummy di zona | 0,9059 |
| **differenza** | **+0,0602** |

Le dummy di zona aggiungono sei punti di varianza spiegata a un modello che ne spiegava già l'84,6%. Il numero va letto insieme a quello della fase 5, dove la macrozona da sola spiegava il 55,6% della varianza del prezzo al metro quadro: i due risultati non si contraddicono, ma rispondono a due domande diverse. Alla domanda su quanto spieghi la posizione presa da sola la risposta è moltissimo; alla domanda su quanto aggiunga a chi conosce già superficie, bagni, stato e piano dell'immobile la risposta è sei punti. La ragione è che una parte dell'informazione geografica è già contenuta nelle caratteristiche stesse degli immobili, dato che quelli grandi e ristrutturati sono distribuiti in modo tutt'altro che uniforme sulla città.

**I limiti, dichiarati senza giri di parole**

- Si tratta di **prezzi richiesti**, non di prezzi di transazione. A Milano lo scarto fra richiesta e rogito è reale e non è costante fra le zone, quindi non è nemmeno un errore che si annulla nei confronti.
- Gli annunci sono un'**istantanea**. Niente di quanto affermato qui riguarda un andamento nel tempo, e i coefficienti non dicono nulla su come si muoveranno i prezzi.
- Tutto è **associativo**. Nessuna pretesa causale viene avanzata, e nessuna è ottenibile da questo disegno: β = 0,079 sull'ascensore non significa che installarne uno faccia salire il prezzo dell'8,2%, ma che gli immobili con ascensore costano in media l'8,2% in più di immobili altrimenti simili. La differenza non è formale — chi ha l'ascensore ha anche, sistematicamente, un edificio di un certo tipo.
- Il modello gira su **14.639 annunci su 16.346**: il 10,4% è escluso dalla listwise deletion, e chi ha i campi incompleti non è un campione casuale degli annunci.
- Restano **assunzioni violate ma dichiarate**: l'eteroschedasticità è ridotta e non eliminata (per questo gli HC3), e i residui hanno una coda sinistra pesante.

### Phase 10 — Mappa del prezzo per zona

**Fase completata.** Il deliverable finale: **`index.html`**, mappa interattiva degli 88 NIL di Milano (*Nuclei d'Identità Locale*), in due viste e con due variabili di prezzo. Nove funzioni orchestrate da `map_phase`. `milano-heatmap.html` resta nel repository come mappa di riferimento da cui è partito il lavoro: non è un output di questa fase e i suoi aggregati non sono quelli calcolati qui.

**Il point-in-polygon non è servito.** Il piano iniziale prevedeva di assegnare ogni annuncio a una zona per intersezione geometrica, dal momento che le 144 microzone e le 32 macrozone presenti nel CSV non coincidono con gli 88 NIL. Il CSV porta però già una colonna `nil_id`, e la verifica di compatibilità è risultata netta: 88 identificativi in comune con il GeoJSON e zero nomi discordanti. L'assegnazione si riduce quindi a un `groupby('nil_id')`, senza bisogno di aggiungere `shapely` o `geopandas` fra le dipendenze. La riga della tabella del dataset che dichiarava `nil_id` come inutilizzata è stata corretta di conseguenza.

| | |
|---|---|
| annunci con zona | **16.333** su 16.346 (13 senza coordinate) |
| zone con almeno un annuncio | 87 su 88 — Stephenson non ne ha nessuno |
| zone rappresentate | **78** |
| zone soppresse | **9**, da 1 a 9 annunci ciascuna |

**La soppressione delle zone piccole.** Colorare una zona significa affermare qualcosa sul suo prezzo, e una media costruita su quattro osservazioni non è confrontabile con una costruita su 834. La soglia è stata fissata a dieci annunci: al di sotto, il blocco resta grigio e piatto e il tooltip riporta la dicitura "dati insufficienti" anziché un numero. Non si tratta di una scelta neutra, e costituisce l'unico punto rimasto aperto della fase: nove zone della città non dicono nulla, e la decisione fra attribuire loro un valore contraendolo verso la media cittadina, abbassare la soglia oppure accorparle alle zone vicine non è ancora stata presa.

**Media o mediana?** La richiesta iniziale riguardava il prezzo medio al metro quadro, ed è quindi la media a governare l'altezza dei blocchi. La mediana non sparisce però dalla mappa: compare nel tooltip insieme all'intervallo fra primo e terzo quartile, ed è lì che si legge l'asimmetria già stabilita nella fase 1. Lo scarto fra le due misure è informativo di per sé: vale mediamente un punto e mezzo percentuale, ma in una zona arriva al 35%, e un divario ampio segnala una zona con pochi immobili molto costosi piuttosto che una zona uniformemente cara.

#### Le due variabili di prezzo

La prima variabile, il **prezzo medio**, è quello effettivamente richiesto nella zona. Ha però il difetto di confondere due informazioni distinte: quanto vale la posizione e quanto valgono gli immobili che vi si trovano. La fase 6 lo aveva già lasciato intuire, dato che fra prezzo medio e superficie media per zona la correlazione vale 0,572.

La seconda variabile, l'**appartamento tipo**, separa le due informazioni. Si ottiene rifittando il modello della fase 8 con le dummy dei NIL anziché delle macrozone, e usandolo poi per prezzare un solo appartamento identico in ciascuna zona.

| | |
|---|---|
| righe | 14.591 |
| zone stimate | **77** |
| R² adjusted | **0,9215** (contro 0,9059 con le macrozone) |
| appartamento di riferimento | 80 m², 3 locali, 1 bagno, ristrutturato, piano 2, ascensore, riscaldamento centralizzato |
| intervallo dei valori | da € 2.630 a € 8.672 /m² |

Le due misure correlano fra loro a 0,98, ma le distanze cambiano, ed è esattamente lì che sta l'informazione utile.

| zona | prezzo medio | appartamento tipo | scarto |
|---|---|---|---|
| Brera | 12.303 | **8.672** | −3.631 |
| Tre Torri | 11.754 | **7.796** | −3.958 |
| Duomo | 11.080 | **8.411** | −2.669 |
| Parco Bosco in Città | 2.904 | **3.736** | **+832** |

Tre Torri perde quasi 4.000 euro al metro quadro e scende dal secondo al terzo posto, scavalcata dal Duomo: il suo prezzo grezzo è gonfiato dal fatto che in quella zona gli appartamenti hanno una superficie media di 179 metri quadri e sono di costruzione recente, non dalla posizione in sé. All'estremo opposto Parco Bosco in Città guadagna terreno, perché il prezzo grezzo la sottostima: vi si vendono case grandi, che al metro quadro costano meno. È la risposta quantificata alla domanda che la fase 9 aveva sollevato senza chiuderla, e cioè che più della metà di quello che sembra un premio di lusso è in realtà il quartiere.

**Il limite di questa variabile, misurato.** L'obiezione più ovvia è che nessun annuncio reale coincide con l'appartamento di riferimento. È la stessa obiezione che si potrebbe muovere al prezzo al metro quadro, e la risposta è la stessa: la costruzione serve a confrontare le zone su basi uguali. Resta però vero che la stima si appoggia al modello tanto più quanto la zona è lontana dal riferimento, e questa distanza si può misurare. La quota di annunci compresi fra 60 e 100 metri quadri vale il 44% nella zona mediana, e solo due zone su 78 scendono sotto il 15%: Parco Sempione con il 9% e Tre Torri con il 10%. Poiché Parco Sempione è già esclusa dal modello per insufficiente numerosità, resta una sola zona, Tre Torri, in cui il numero è più un'estrapolazione del modello che una lettura dei dati di quella zona, e va letto sapendolo.

#### Le due viste

Nella vista **3D** altezza e colore portano due variabili diverse: l'altezza rappresenta il prezzo e il colore la superficie media, suddivisa in cinque classi per quantile con tagli a 81, 88, 94 e 107 metri quadri. Si tratta quindi di una mappa bivariata, capace di mostrare qualcosa che una mappa a una sola variabile non potrebbe: dove si trovino gli appartamenti cari e piccoli e dove quelli economici e grandi. Il risultato è che il primo caso non esiste affatto, perché nessuna zona presenta insieme appartamenti piccoli e prezzi alti. A Milano non si paga il metro quadro caro per stare stretti.

Nella vista **2D piatta**, non essendoci più l'altezza, è il colore a farsi carico del prezzo, sempre in cinque classi per quantile ricalcolate su ciascuna delle due variabili di prezzo. È una rappresentazione meno spettacolare e più precisa, perché nessuna zona può coprirne un'altra.

In entrambe le viste le classi sono definite per quantile e non a intervalli uguali, perché su una distribuzione asimmetrica gli intervalli uguali produrrebbero quattro classi quasi vuote e una che contiene tutto il resto.

| variabile | tagli delle 5 classi |
|---|---|
| superficie media (m²) | 81 · 88 · 94 · 107 |
| prezzo medio (€/m²) | 3.498 · 4.280 · 5.114 · 7.019 |
| appartamento tipo (€/m²) | 3.648 · 4.208 · 4.809 · 5.910 |

#### Le scelte di rappresentazione, e perché

L'altezza parte sempre da zero. Sottrarre il minimo per far risaltare le differenze farebbe sembrare una zona da 6.000 euro al metro quadro il doppio di una da 5.000, il che sarebbe una rappresentazione ingannevole. Il fattore di scala vale 0,3 ed è dichiarato in legenda: la zona più cara risulta così alta circa 3,7 chilometri su una città larga diciotto.

L'altezza vista in prospettiva non è però una scala di misura affidabile. Un blocco lontano sembra più basso di uno vicino di pari altezza, i blocchi alti nascondono quelli che stanno dietro, e l'area del poligono, che non significa nulla, finisce per acquistare peso visivo. Da questa consapevolezza discendono tre contromisure: una classifica testuale di tutte le zone, dove i confronti si leggono davvero; il tooltip con i numeri esatti; e la vista 2D, che elimina il problema alla radice.

Selezionando una zona, dalla classifica oppure cliccandola direttamente sulla mappa, le altre scendono a un terzo della loro altezza e si attenuano, la mappa ruota automaticamente sul lato che presenta meno massa alta davanti alla zona scelta, e un cartellino ne riporta nome e valore. Si tratta di una messa a fuoco temporanea, nella quale la zona selezionata conserva la propria altezza vera. Per tornare alla vista d'insieme basta cliccare fuori dalle zone oppure premere Esc.

Il fondo è scuro in entrambe le viste. Il primo tentativo era stato fatto su fondo chiaro con bordi bianchi fra i blocchi, ma i bordi risultavano invisibili e i blocchi finivano per impastarsi l'uno nell'altro. Entrambe le rampe di colore sono sequenziali a tinta unica, arancio per la superficie e blu per il prezzo, e vanno dal chiaro allo scuro al crescere del valore, con ogni passo verificato per un contrasto di almeno 3:1 contro il fondo. Questo limite è reale e ha vincolato la scelta: un passo più scuro di `#a05520` sull'arancio, o di `#256abf` sul blu, scende sotto la soglia e la classe più alta comincia a sparire nello sfondo.

Lo zoom in allontanamento è infine bloccato al livello 10, appena sotto quello della vista d'insieme: non essendoci alcuna mappa stradale sotto le zone, allargare oltre rimpicciolirebbe soltanto Milano dentro uno schermo vuoto.

#### Il file

Il file `index.html` pesa 2,71 MB ed è completamente autonomo, perché vi sono incorporati sia la libreria di rendering — deck.gl 9.4.0, nel file `deck.min.js`, con la versione fissata esattamente come per le dipendenze Python — sia il GeoJSON delle 88 zone. Non effettua alcuna richiesta di rete e non scarica alcun tile cartografico: si apre con un doppio clic e funziona offline.

Vale la pena chiarire che cosa la mappa non è. È un colpo d'occhio e non uno strumento di misura, funzione per la quale esistono la classifica e il tooltip. Restano inoltre validi tutti i limiti dichiarati nella fase 9: si tratta di prezzi richiesti e non di transazione, di un'istantanea e non di un andamento, e di relazioni associative e non causali.

---

## Che cosa viene dopo: la dashboard

Le fasi dalla 1 alla 10 rispondono a una domanda sui dati che ci sono. Le quattro fasi qui sotto rispondono a una domanda a cui quei dati non possono rispondere da soli, perché introducono una seconda fonte — e finiscono in qualcosa di pubblicabile, non in un grafico.

La premessa è la debolezza che la fase 9 ha dichiarato senza mai risolverla: **questi sono i prezzi che i venditori chiedono, non quelli che i compratori pagano.** L'Agenzia delle Entrate pubblica due volte l'anno le quotazioni OMI, che derivano dagli atti registrati e descrivono quindi quanto si conclude davvero. La differenza fra le due, zona per zona, è un numero che nessuno pubblica e che serve a chiunque compri, venda o faccia mediazione a Milano: *in questo quartiere si chiede il dodici per cento più di quanto si conclude.*

Queste fasi **non sono ancora state svolte**. Quello che segue è il piano, scritto prima del lavoro e non dopo, compresi i tre punti in cui è più probabile che vada storto.

### Fase 11 — Le quotazioni OMI, la seconda fonte

**Pianificata.** La fonte pubblica, per provincia e per zona OMI, un prezzo minimo e uno massimo al metro quadro per ogni combinazione di tipologia — *abitazioni civili*, *economiche*, *di tipo signorile*, *ville* — e stato di conservazione — *normale*, *ottimo*, *scadente*. Vale la pena notare che cosa significa: non una stima puntuale ma una fascia, e una fascia che viene rivista ogni semestre, quindi il semestre usato va registrato accanto a ogni numero che ne deriva.

In questa fase ci sono tre trappole, e tutte tre sono metodologiche e non tecniche, che è esattamente ciò che le rende facili da imboccare.

**La definizione di superficie non è la stessa nelle due fonti.** L'OMI quota al metro quadro di *superficie lorda*, che comprende i muri e una quota delle parti comuni; i portali di annunci quotano la *superficie commerciale*, e a volte qualcosa di più vicino al netto. Confrontarle come se fossero la stessa misura gonfia il divario di una quantità sistematica che non ha niente a che vedere con il mercato: è un artefatto di definizioni. O si applica la conversione e la si dichiara, oppure il confronto resta rigorosamente relativo.

**Una fascia non è un numero.** Schiacciare una cella OMI sul suo valore centrale e pubblicare una singola percentuale butta via l'incertezza che la fonte dichiara da sé. Qualunque cosa si mostri, la fascia le viaggia accanto.

**Tipologia e stato vanno abbinati, non dati per scontati.** Confrontare tutti gli annunci contro *abitazioni civili, stato normale* ci mescola dentro in silenzio il segmento di lusso, che la fase 8 ha stabilito valere +44% da solo. La costruzione dell'appartamento di riferimento della fase 10 risolve già il problema, e vale la pena capire perché: fissando l'immobile e lasciando variare solo la posizione, produce esattamente l'oggetto che una cella OMI quota.

### Fase 12 — Unire due geografie che non coincidono

**Pianificata.** Nella fase 10 è andata bene. Il CSV portava già una colonna `nil_id`, quindi assegnare gli annunci alle zone si è ridotto a un `groupby` e non sono serviti né `shapely` né `geopandas`. Quella fortuna non si ripete: l'OMI ha una sua zonizzazione, con codici e fasce propri, e non coincide con gli 88 NIL. È la più difficile delle quattro fasi e il punto in cui è più probabile che tutto vada storto senza farsi notare.

L'unione è areale e non puntuale, perché due insiemi di poligoni suddividono la stessa città in modo diverso e un valore definito su uno va riespresso sull'altro. Il metodo difendibile è l'interpolazione ponderata per area — per ogni NIL, le zone OMI che lo intersecano, pesate per l'area di sovrapposizione — e poggia su un'assunzione che conviene dire a voce alta invece di seppellirla: che il prezzo sia uniforme dentro una zona OMI. Non lo è. È esattamente per questo che le zone OMI esistono.

Quindi questa fase produce due cose, non una. La tabella di corrispondenza, e **una misura di quanto fidarsi di ogni sua riga**: per ciascun NIL, su quante zone OMI si appoggia e che quota della sua area copre quella dominante. Dove un NIL sta pulito dentro una sola zona OMI il numero che ne esce è solido; dove è ricucito da quattro, è una media di medie e va marcato come tale invece di essere colorato come se fosse una misura. È la stessa disciplina della soglia dei dieci annunci della fase 10, applicata a un modo diverso di sbagliare.

È anche la fase che introduce la prima vera dipendenza geometrica del progetto, `geopandas` e `shapely`, che vanno in `requirements.txt` fissate esattamente come tutto il resto.

### Fase 13 — Il divario fra chiesto e concluso

**Pianificata.** Una volta che le due fonti stanno sulla stessa geografia il divario è una sottrazione, ed è tutto il senso dell'operazione. Da qui devono uscire quattro cose.

Il divario per NIL, **come fascia e non come punto**, con accanto sia il semestre OMI sia la data degli annunci.

La classifica, perché il risultato interessante non è la media cittadina ma la dispersione. Se il divario risultasse più o meno uniforme su Milano, è un risultato noioso e va riportato come noioso. Se varia di un fattore due fra una zona e l'altra, quello è il titolo.

Una verifica sul confondimento ovvio. Gli annunci catturano l'offerta ancora *invenduta*, e quindi sovrarappresentano gli immobili che sono rimasti a lungo sul mercato: una zona con un divario ampio può essere semplicemente una zona in cui si vende lentamente, non una in cui i venditori sono ottimisti. La fase 9 aveva già dichiarato questo limite in generale; qui diventa una cosa che si può effettivamente mettere alla prova, contro l'ampiezza della fascia OMI e la quota di annunci vecchi.

E il problema dei piccoli campioni, che torna identico. Le nove zone sotto i dieci annunci non possono portare un divario credibile, e non possono portarlo nemmeno le zone il cui abbinamento OMI è ricucito da molti frammenti. Entrambe vengono soppresse, con la stessa logica e con le stesse parole della fase 10.

Qui due esiti negativi sono possibili ed entrambi sono pubblicabili: il divario può essere quasi costante in tutta la città, oppure troppo rumoroso per sostenere qualunque affermazione. In entrambi i casi si scrive con la stessa chiarezza con cui si scriverebbe un risultato positivo.

### Fase 14 — La dashboard

**Pianificata.** Il deliverable pubblicato, e il momento in cui il lavoro smette di essere un'analisi e diventa una cosa utilizzabile da chi non aprirà mai un notebook. Va dove la mappa sta già, alla radice del sito Pages.

Il perimetro è volutamente stretto — quattro cose, e nient'altro:

1. la mappa, con il divario chiesto-OMI come terza variabile di prezzo accanto alle due della fase 10
2. la classifica del divario in testo leggibile, perché l'altezza vista in prospettiva non è uno strumento di misura: la lezione che la fase 10 ha già pagato
3. l'effetto delle caratteristiche dell'immobile a parità di zona, che la fase 8 ha stimato e che finora non è mostrato da niente
4. una pagina che dica da dove vengono i dati, aggiornati a quando, e che cosa non dicono

Quello che resta fuori è altrettanto importante. Nessun filtro dal vivo che ricalcola a richiesta, nessun server, e niente che si addormenti dopo dieci minuti di inattività e faccia poi aspettare trenta secondi a chi ha appena cliccato un link che gli è stato appena mandato. La scelta tecnica è quella noiosa e resta quella noiosa: precalcolare in Python, scrivere un JSON, servire una pagina statica. Funziona già per un file autonomo da 2,71 MB, e la proprietà per cui la mappa non fa alcuna richiesta di rete deve sopravvivere a questa fase, non esserci barattata dentro.

Pubblicata batte perfetta. Una versione che esiste e che è onesta sui propri limiti vale più di una che si sta ancora limando.

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
| 9. Statistical Conclusions | ✅ **completata** — effetti, IC, limiti dichiarati |
| 10. Mappa del prezzo per zona | ✅ **completata** — mappa 3D/2D interattiva, 78 zone, appartamento tipo |
| 11. Quotazioni OMI | 🔲 **pianificata** — seconda fonte, derivata dagli atti registrati |
| 12. Corrispondenza OMI ↔ NIL | 🔲 **pianificata** — unione ponderata per area, con la sua qualità misurata |
| 13. Divario chiesto/concluso | 🔲 **pianificata** — per zona, come fascia, confondimento verificato |
| 14. Dashboard | 🔲 **pianificata** — pubblicata, quattro pannelli, sempre senza server |

---

## Struttura del progetto

```
milano_real_estate_analysis/
├── milano_analysis.py                  # script di analisi — pulizia + fasi 1-10
├── immobiliare_milano_vendita.csv      # dataset (18.017 × 31)
├── milano_zone_NIL.geojson             # 88 poligoni NIL — input della fase 10
├── index.html                          # mappa interattiva — output della fase 10
├── deck.min.js                         # deck.gl 9.4.0, incorporato nella mappa
├── milano-3d.html                      # redirect, tiene in vita il vecchio link
├── milano-heatmap.html                 # mappa 2D di riferimento di partenza
├── charts/                             # figure delle fasi 1-8 in PNG (14 file)
├── REPORT.it.md                        # resoconto dei risultati, per chiunque
├── REPORT.md                           # versione inglese
├── README.md                           # versione inglese
└── README.it.md
```

Dataset, geometrie e libreria di rendering si trovano già nella cartella del progetto, quindi lo script di analisi può usare percorsi relativi e va lanciato dalla cartella stessa.

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

# fase 9 — orchestrate da conclusions_phase
conclusions_table         → coefficienti, IC 95%, p-value, flag di significatività
zone_variance_share       → R² adj con e senza zona, e la differenza

# fase 10 — orchestrate da map_phase
prepare_map_data          → solo gli annunci con nil_id        16.346 → 16.333
zone_aggregates           → n, media, mediana, p25, p75, prezzo e superficie per NIL
suppress_small_zones      → zone sotto i 10 annunci marcate, non colorate
location_premium          → OLS con dummy dei NIL, poi lo stesso appartamento
                            prezzato in ogni zona
value_classes             → tagli delle 5 classi per quantile, una per variabile
build_zone_geojson        → properties del GeoJSON riscritte con i propri aggregati
map_metadata              → riepilogo, tagli, appartamento di riferimento
write_3d_map              → deck.gl + GeoJSON incorporati in index.html
```

La fase 8 restituisce `regression_data` insieme al modello stimato, che il programma principale passa alla fase 9: in questo modo le conclusioni si leggono dal modello già stimato anziché rifittarlo una seconda volta.

Ogni trasformazione è preceduta dalla propria ispezione, secondo il principio di guardare com'è fatta una colonna prima di modificarla. È il motivo per cui ci si è accorti in tempo che il secondo e il terzo passaggio della pulizia sarebbero risultati in gran parte a vuoto.

### Strumenti

`pandas` e `numpy` per il lavoro sui dati (`numpy` già in uso per la trasformazione logaritmica della fase 2), `scipy.stats` per le fasi 2-6 (già in uso per il Q-Q plot, per le curve normali sovrapposte agli istogrammi e per i valori critici *t* della fase 3), `statsmodels` per le fasi 5, 7 e 8 — in uso con `statsmodels.api`, `anova_oneway`, `pairwise_tukeyhsd`, `het_breuschpagan` e `variance_inflation_factor` —, `matplotlib` per i grafici e `seaborn` per la sola heatmap della fase 6. La fase 10 non aggiunge dipendenze Python — usa `json` dalla libreria standard — e affida il rendering della mappa a **deck.gl 9.4.0**, incorporato nel file di output.

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
