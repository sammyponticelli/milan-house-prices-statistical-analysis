# Milano Real Estate — Analisi Statistica

**Quali fattori influenzano il prezzo delle case a Milano, e cosa può dirci l'analisi statistica sul mercato immobiliare?**

L'analisi lavora su ~18k annunci di vendita raccolti da immobiliare.it e percorre l'intero strumentario statistico — dalla statistica descrittiva alla regressione lineare multipla — per arrivare a una **mappa del prezzo medio al metro quadro per zona**.

Il resoconto dei risultati sarà in **[REPORT.md](REPORT.md)**. Questo file documenta i dati, il metodo e il piano di lavoro.

> Il README è scritto in italiano durante lo sviluppo; verrà tradotto in inglese a progetto concluso.

---

## Dataset

`immobiliare_milano_vendita.csv` — **18.017 righe × 29 colonne**, annunci di vendita residenziale a Milano.

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
| `url`, `title`, `address` | Testo libero / identificativi |
| `city`, `region` | Costanti (`Milano` / `Lombardia`) |
| `category` | `Residenziale` (16.469), `Nuove costruzioni` (137), `Palazzi - Edifici` (135) — usata come **filtro**, non come variabile |
| `agency` | Agenzia venditrice (569 mancanti) — possibile estensione, fuori dal modello principale |
| `is_outlier`, `price_is_range` | Flag di qualità già presenti nella sorgente — usati come **filtri** |

---

## Pulizia dei dati

Cinque decisioni, applicate prima di calcolare qualunque statistica.

**1. Eliminare le sotto-unità.** Gli annunci multi-unità (progetti di nuova costruzione) compaiono come una riga padre `unit = 0` più una riga per appartamento `unit = 1, 2, 3…`, **tutte con lo stesso `price` ripetuto**. Contarle significherebbe contare fino a 37 volte un unico prezzo. Le righe delle sotto-unità non hanno `category`, quindi il filtro `category == 'Residenziale'` le rimuove di conseguenza; il filtro viene comunque applicato in modo esplicito, così l'intenzione resta visibile nel codice.

**2. Applicare i flag di qualità della sorgente.** Si scartano `is_outlier == 1` (1.567 righe) e `price_is_range == 1` (1.321 righe). Il secondo è importante: un annuncio il cui prezzo è un *intervallo* ha un `price` che non è un'osservazione reale.

**3. Scartare le righe senza prezzo o superficie.** `price`, `surface_mq`, `price_per_mq` sono le tre variabili da cui dipende tutto il resto.

**4. `elevator` — il mancante significa "no".** La colonna assume i valori `1.0` (13.572) e `NaN` (4.445), senza alcuno zero. Non è una colonna con dei buchi: è una codifica a sola-presenza, il campo viene scritto solo quando l'annuncio dichiara l'ascensore. Viene quindi ricodificata in una dummy 0/1 pulita.

L'alternativa — trattare i `NaN` come dato mancante vero — comporterebbe l'esclusione automatica di **4.445 annunci, il 27% del dataset**, dalla regressione della fase 8. Ed è un'esclusione non casuale: gli annunci col campo vuoto sono sistematicamente immobili più vecchi, piccoli e periferici, cioè proprio il segmento che serve per stimare l'effetto dell'ascensore. Si perderebbero i dati *e* si introdurrebbe una distorsione, invece di evitarla.

Il rischio residuo della codifica scelta è che qualche immobile abbia davvero l'ascensore senza che il campo sia compilato. Quei casi finiscono etichettati come "senza" e **attenuano** β₅ verso lo zero: la stima dell'effetto risulta più piccola del vero, mai più grande. È un errore conservativo. La fase 8 lo verifica con un'analisi di sensibilità esplicita (vedi sotto) anziché limitarsi a dichiarare l'assunzione.

**5. Parsare le colonne testuali sporche.** `rooms` (`5+` → 5, `2 - 4` → scartato, dato che gli intervalli compaiono solo sulle righe multi-unità già rimosse), `bathrooms` (`3+` → 3), `floor` (`piano terra` → 0, `piano rialzato` → 0,5, `3 piano` → 3).

**Risultato: 16.346 annunci puliti** (90,7% del file grezzo), di cui **16.333 geolocalizzati**. Tutte e 32 le macrozone sopravvivono con almeno 115 annunci ciascuna — abbastanza per i confronti fra gruppi delle fasi 4-5 senza dover accorpare categorie.

---

## Struttura dell'analisi

### Phase 1 — Descriptive Statistics

Media, mediana, moda, varianza, deviazione standard, quartili, range e coefficiente di variazione, calcolati sulle tre variabili centrali: `price`, `surface_mq`, `price_per_mq`.

Il punto della fase è il confronto **fra** le variabili, non i numeri in sé:

| | media | mediana | CV | asimmetria |
|---|---|---|---|---|
| `price` | € 570.105 | € 379.000 | **1,18** | 5,68 |
| `surface_mq` | 95 m² | 80 m² | 0,67 | 3,42 |
| `price_per_mq` | € 5.622 | € 5.073 | **0,47** | 1,83 |

Due cose da leggerci dentro. Primo, media ≫ mediana ovunque: le distribuzioni sono asimmetriche a destra e **la media non è un buon riassunto dell'annuncio milanese tipico** — una manciata di immobili sopra i 10 M€ la trascina in alto della metà. Secondo, il coefficiente di variazione scende da 1,18 a 0,47 una volta normalizzato il prezzo per la superficie: gran parte della variabilità grezza del prezzo è semplicemente variabilità di dimensione. È il primo vero risultato del progetto, e giustifica l'uso di `price_per_mq` come variabile di confronto dalla fase 4 in avanti.

### Phase 2 — Probability & Distributions

- Distribuzione empirica e **istogrammi** di `price` e `price_per_mq`, con media e mediana marcate sul grafico perché l'asimmetria si veda.
- **Percentili** (p1, p5, p10, p25, p50, p75, p90, p95, p99) — su una distribuzione come questa una tabella di percentili è molto più informativa di una media.
- Confronto con la **distribuzione normale**: curva normale sovrapposta all'istogramma, **Q-Q plot**, asimmetria e curtosi.
- **Trasformazione logaritmica.** `log(price)` ha un'asimmetria di **0,66** contro 5,68 del prezzo grezzo — abbastanza vicina alla simmetria da rendere difendibile l'apparato parametrico delle fasi 4-8. Le due scale vengono mostrate affiancate.

Una nota di metodo: con n = 16.346 i test formali di normalità (Shapiro-Wilk, D'Agostino) rifiutano l'ipotesi nulla su qualunque dataset, perché la potenza nel rilevare una deviazione irrilevante è di fatto pari a 1. La fase si appoggia quindi ai **Q-Q plot e agli indici di forma**, spiegando perché il test non viene usato.

### Phase 3 — Sampling & Confidence Intervals

Questa fase tratta i 16.346 annunci puliti come **popolazione** — i suoi parametri sono noti — e ne estrae campioni, così che stima e verità siano effettivamente confrontabili.

- **Distribuzione della media campionaria**: 1.000 campioni casuali con n = 30, n = 100, n = 500; istogramma delle medie campionarie per ciascuna numerosità.
- **Teorema del limite centrale in pratica**: la distribuzione della media campionaria assume forma normale anche se la distribuzione dei prezzi sottostante è fortemente asimmetrica, e la sua dispersione si riduce del fattore atteso √n. Confronto fra errore standard empirico e σ/√n teorico.
- **Intervalli di confidenza al 95%** per il prezzo medio al m², per ciascuna numerosità campionaria, usando la distribuzione *t*.
- **Verifica della copertura**: sui 1.000 campioni, quanti intervalli contengono davvero la media della popolazione? Il risultato deve attestarsi vicino al 95%, ed è la dimostrazione più diretta dell'intero progetto di che cosa *significhi* un livello di confidenza — un'affermazione sulla procedura, non sul singolo intervallo.

### Phase 4 — Hypothesis Testing

Confronti formali fra due campioni su `price_per_mq`.

**Test 1 — due zone.**

> **H₀**: μ(zona A) = μ(zona B) — il prezzo medio al m² è uguale nelle due zone
> **H₁**: μ(zona A) ≠ μ(zona B) — bilaterale

Si testano due coppie, scelte apposta per contrasto: una coppia lontanissima (`Centro`, n = 389, contro `Bisceglie, Baggio, Olmi`, n = 426) dove l'esito è scontato e la quantità interessante è la **dimensione dell'effetto**, non il p-value; e una coppia ravvicinata di macrozone di fascia media confrontabile, dove il test fa un lavoro vero.

**Test 2 — una caratteristica dell'immobile.** Stesso apparato applicato a `elevator` (con ascensore contro senza) e a `condition` (`Da ristrutturare` contro `Ottimo / Ristrutturato`), per mostrare che la verifica d'ipotesi non riguarda solo la geografia.

Per ogni test si riportano: **statistica t, gradi di libertà, p-value, livello di significatività α = 0,05, intervallo di confidenza per la differenza fra le medie e d di Cohen**. Si usa il **t-test di Welch** anziché quello di Student, dato che la varianza in `Centro` non ha nulla a che vedere con quella in periferia, e si riporta il test di Levene a giustificarlo.

La discussione copre l'**errore di tipo I** (rifiutare una H₀ vera — il 5% che accettiamo fissando α), l'**errore di tipo II** e il motivo per cui un n grande rende "significative" differenze minuscole e prive di senso: con centinaia di annunci per zona, uno scarto di 50 €/m² può superare p < 0,05 senza significare nulla per chi compra. Da qui la dimensione dell'effetto accanto a ogni p-value.

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
| 0. Pulizia dei dati | ⬜ da fare |
| 1. Descriptive Statistics | ⬜ da fare |
| 2. Probability & Distributions | ⬜ da fare |
| 3. Sampling & Confidence Intervals | ⬜ da fare |
| 4. Hypothesis Testing | ⬜ da fare |
| 5. ANOVA | ⬜ da fare |
| 6. Correlation | ⬜ da fare |
| 7. Linear Regression | ⬜ da fare |
| 8. Multiple Linear Regression | ⬜ da fare |
| 9. Statistical Conclusions | ⬜ da fare |
| 10. Mappa del prezzo medio al m² per zona | ⬜ da fare — mappa di riferimento già disponibile |

---

## Struttura del progetto

```
milano_real_estate_analysis/
├── milano_analysis.py                  # script di analisi
├── immobiliare_milano_vendita.csv      # dataset (18.017 × 29)
├── milano-heatmap.html                 # mappa per zona — output della fase 10
├── charts/                             # figure, salvate in PNG
├── REPORT.md                           # resoconto dei risultati
└── README.md
```

Dataset e mappa sono già nella cartella: lo script di analisi può usare percorsi relativi.

### Strumenti

`pandas` e `numpy` per il lavoro sui dati, `scipy.stats` per le fasi 3-6, `statsmodels` per le fasi 5, 7 e 8, `matplotlib` per i grafici.

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
