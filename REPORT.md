# Quanto costano le case a Milano, e perché

Questo documento riassume i risultati di un'analisi statistica condotta su 16.346 annunci di vendita di immobili a Milano, estratti dal portale immobiliare.it il **26 agosto 2026**. La domanda di partenza è semplice: da che cosa dipende il prezzo di una casa a Milano, e quanto pesa ciascun fattore rispetto agli altri?

Il testo è pensato per essere letto senza conoscenze di statistica. Chi volesse il dettaglio dei metodi, delle verifiche e del codice lo trova nel [README](README.md), che accompagna passo per passo tutte le dieci fasi del lavoro.

Prima di cominciare, due precisazioni che valgono per tutto quello che segue. I prezzi analizzati sono quelli richiesti dai venditori negli annunci, non quelli effettivamente pagati al momento del rogito. E si tratta di una fotografia scattata in un solo giorno, il 26 agosto 2026, non di una serie storica: niente di quanto scritto qui riguarda l'andamento dei prezzi nel tempo, né consente di prevederlo.

---

## I risultati principali

L'analisi arriva a sei conclusioni, che le sezioni successive spiegano una per una.

La superficie è il fattore che pesa più di ogni altro, ma il suo effetto non è proporzionale: le case grandi costano più che proporzionalmente rispetto a quelle piccole. Il quartiere, da solo, spiega più della metà delle differenze di prezzo al metro quadro fra un annuncio e l'altro, ed è quindi il secondo fattore in ordine di importanza. Proprio per questo, buona parte di ciò che appare come valore "di lusso" si rivela essere il valore dell'indirizzo: tenendo conto del quartiere, il premio del segmento di lusso si dimezza.

Ci sono poi due risultati negativi, cioè due cose che ci si aspetterebbe contassero e invece non contano. Il numero di locali non ha alcun effetto sul prezzo una volta che si conoscono la superficie e il quartiere, e lo stesso vale per il tipo di riscaldamento.

Infine, due osservazioni sulla geografia della città. Milano non è divisa fra un centro e una periferia: passando dalla zona più economica alla più cara si sale in modo continuo, senza salti. E il prezzo medio di una zona non è un'informazione pura, perché mescola quanto vale la posizione con quanto valgono le case che vi si trovano; separare le due cose cambia la classifica dei quartieri.

---

## Il mercato visto dall'alto

Il punto di partenza è capire come sono distribuiti i prezzi, perché da questo dipende quale numero abbia senso usare per riassumerli.

| | media | mediana |
|---|---|---|
| prezzo | € 570.105 | € 379.000 |
| superficie | 95 m² | 80 m² |
| prezzo al m² | € 5.622 | € 5.073 |

La distanza fra le due colonne non è un dettaglio contabile, ma il primo risultato dell'analisi. La mediana è il valore che divide esattamente a metà gli annunci: metà delle case in vendita a Milano costa meno di 379.000 euro. La media, invece, è di 570.105 euro, cioè quasi il cinquanta per cento più alta, e la ragione è che una minoranza di immobili molto costosi la trascina verso l'alto.

Quanto sia ristretta questa minoranza si vede guardando i due estremi della distribuzione. Il dieci per cento più caro degli annunci parte da 1,09 milioni di euro, mentre l'uno per cento più caro parte da 3,5 milioni: fra questi due gradini ci sono quasi due milioni e mezzo di euro. Il mercato di fascia alta milanese è insomma un segmento a sé, con una dinamica propria, e ogni volta che si cita "il prezzo medio a Milano" si sta usando un numero che quel segmento ha spostato in modo consistente.

Per questa ragione l'analisi ragiona quasi sempre in termini di prezzo al metro quadro anziché di prezzo assoluto. Dividere il prezzo per la superficie elimina la variabile più ovvia — le case grandi costano di più, il che non è una scoperta — e lascia emergere tutto il resto. L'effetto di questa divisione è misurabile: la variabilità dei prezzi si riduce di più della metà. Detto in altri termini, gran parte del motivo per cui due case hanno prezzi diversi è semplicemente che una è più grande dell'altra.

---

## Che cosa determina il prezzo

Per rispondere alla domanda iniziale è stato costruito un modello statistico che considera tutte le caratteristiche di un immobile contemporaneamente, invece di esaminarle una alla volta. La differenza fra i due approcci è sostanziale, e conviene mostrarla con un esempio concreto.

Guardando i dati grezzi, le case dotate di ascensore costano in media 1.121 euro al metro quadro in più di quelle che ne sono prive. Sarebbe però sbagliato concludere che l'ascensore valga quella cifra, perché le case con ascensore si trovano tipicamente in palazzi più recenti e in zone più centrali, e differiscono dalle altre sotto molti aspetti insieme. La domanda corretta è: quanto vale l'ascensore fra due case identiche sotto ogni altro profilo?

Il modello risponde proprio a questa domanda, perché stima l'effetto di ciascuna caratteristica tenendo ferme tutte le altre. Il risultato è che, a parità di zona, superficie, stato di conservazione e tutto il resto, l'ascensore vale un aumento di prezzo dell'8,2 per cento. Il resto della differenza osservata nei dati grezzi non era l'ascensore: era il quartiere e il tipo di edificio in cui l'ascensore si trova.

Applicando lo stesso ragionamento a tutte le caratteristiche disponibili si ottiene il quadro seguente, ordinato dal fattore più influente al meno influente.

| caratteristica | effetto sul prezzo, a parità di tutto il resto |
|---|---|
| superficie | ogni +1% di superficie corrisponde a +0,80% di prezzo |
| appartenenza al segmento di lusso | +44% |
| un bagno in più | +9,3% |
| un gradino nella scala dello stato di conservazione | +8,4% |
| presenza dell'ascensore | +8,2% |
| ogni piano di altezza in più | +1,2% |
| numero di locali | nessun effetto rilevabile |
| tipo di riscaldamento | nessun effetto rilevabile |

Nel complesso, il modello riesce a spiegare il 91 per cento delle differenze di prezzo fra un annuncio e l'altro. È un risultato molto solido, e significa che la superficie, la zona e una manciata di caratteristiche dell'immobile bastano quasi interamente a determinare quanto costa una casa a Milano: lo spazio lasciato a fattori non osservati è ridotto.

### I due risultati controintuitivi

Il primo riguarda il numero di locali, che non influenza il prezzo in alcun modo apprezzabile. A parità di superficie, di numero di bagni e di quartiere, avere tre stanze anziché due non cambia quanto costa la casa. Non si tratta di un risultato incerto per mancanza di dati: il modello stabilisce che l'effetto reale è compreso fra −0,9% e +0,5%, escludendolo quindi in entrambe le direzioni. Quello che si paga sono i metri quadri, non il modo in cui vengono suddivisi.

C'è anche una spiegazione per il fatto che, prima di considerare il quartiere, il numero di locali sembrava invece contare qualcosa. Gli appartamenti tagliati in molte stanze piccole sono caratteristici di certe zone della città, e quindi il numero di locali stava funzionando da indicatore indiretto della posizione, non da caratteristica dotata di un valore proprio. Quando la posizione entra esplicitamente nel modello, quell'informazione diventa superflua.

Il secondo risultato riguarda il piano ed è il caso opposto. Senza tenere conto della zona, il piano sembrava non contare quasi nulla; una volta introdotto il controllo per il quartiere, il suo effetto si quadruplica. La ragione è che i palazzi alti si trovano tanto nei quartieri più costosi quanto nelle periferie di edilizia popolare, e i due gruppi si annullavano a vicenda mascherando l'effetto reale. È un caso in cui guardare i dati con più attenzione non ridimensiona un effetto, ma lo fa emergere.

---

## Il peso dell'indirizzo

Se c'è un risultato che l'analisi stabilisce senza margini di ambiguità, è quanto conti la posizione.

Confrontando fra loro le 32 macrozone in cui è suddivisa la città, si scopre che la sola appartenenza a una zona spiega il 55,6 per cento della variabilità del prezzo al metro quadro. Vale la pena soffermarsi su cosa significhi: dopo aver già tolto di mezzo la superficie — perché si ragiona al metro quadro — più della metà di ciò che distingue un annuncio da un altro è pura geografia.

Il divario fra gli estremi è di 3,6 volte: si passa dai 3.216 euro al metro quadro della zona di Bisceglie, Baggio e Olmi agli 11.481 euro del Centro.

Sarebbe però un errore concludere che la città sia divisa in due blocchi. Mettendo in fila tutte e 32 le zone dalla più economica alla più cara si ottiene una salita continua, in cui non compare alcun salto che separi un "centro" da una "periferia". Milano, sul prezzo al metro quadro, è un gradiente.

Questo gradiente ha però una forma asimmetrica. La prima dozzina di zone si concentra in una fascia molto stretta, fra i 3.200 e i 4.500 euro al metro quadro: dodici zone diverse separate da appena 1.300 euro complessivi. Le ultime quattro, invece, coprono da sole quasi 2.000 euro. In fondo alla classifica i quartieri si somigliano al punto che spesso non è possibile distinguerli statisticamente l'uno dall'altro; in cima si distanziano rapidamente.

C'è infine un terzo aspetto, meno immediato ma altrettanto solido: più una zona è cara, più è imprevedibile al proprio interno. Nelle zone periferiche i prezzi sono compressi in una fascia ristretta, mentre in centro la stessa fascia è circa cinque volte più ampia. Comprare in centro non significa soltanto pagare di più, ma anche entrare in un mercato in cui i prezzi di due immobili apparentemente simili possono divergere in misura considerevole.

### Metà del valore "di lusso" è in realtà l'indirizzo

Il risultato più istruttivo emerge confrontando lo stesso modello stimato due volte, una senza e una con l'informazione sul quartiere.

| | senza informazione sul quartiere | con informazione sul quartiere |
|---|---|---|
| premio del segmento di lusso | +97% | +44% |
| premio dell'ascensore | +12,7% | +8,2% |

Il premio associato al segmento di lusso si dimezza. Quello che nel primo modello appariva come il valore di un immobile di pregio era, per più della metà, semplicemente il valore del quartiere in cui quell'immobile si trova. Lo stesso meccanismo, in misura minore, riguarda l'ascensore.

---

## La mappa

Il risultato conclusivo del lavoro è una mappa interattiva della città, contenuta nel file `milano-3d.html`, che si apre con un doppio clic in qualunque browser e funziona anche senza connessione a internet. La città è suddivisa negli 88 quartieri ufficiali del Comune di Milano, i cosiddetti NIL o Nuclei d'Identità Locale.

Ogni quartiere è rappresentato da un blocco la cui altezza corrisponde al prezzo. La mappa può essere consultata in tre dimensioni oppure in versione piatta, e passando il puntatore sopra una zona se ne leggono i valori esatti.

La mappa copre 16.333 annunci sui 16.346 disponibili, e rappresenta 78 delle 88 zone. Le dieci zone escluse meritano una spiegazione: nove hanno meno di dieci annunci ciascuna e una, Stephenson, non ne ha nemmeno uno. Sono lasciate in grigio anziché colorate, perché un prezzo calcolato su quattro immobili non è confrontabile con uno calcolato su ottocento, e colorarle allo stesso modo delle altre significherebbe far apparire come un dato quella che è poco più di un'impressione.

### Perché il prezzo medio di una zona è ambiguo

La parte più interessante della mappa nasce da un problema di interpretazione.

Il prezzo medio di un quartiere mescola due informazioni distinte: quanto vale trovarsi in quel punto della città, e come sono fatte le case che vi si trovano. Le due cose non sono indipendenti, perché nelle zone più costose le case sono anche mediamente più grandi e più ristrutturate. Di conseguenza il prezzo medio fa apparire quelle zone ancora più care di quanto la sola posizione giustificherebbe.

Per separare i due effetti la mappa offre una seconda lettura, che consiste nel calcolare quanto costerebbe uno stesso identico appartamento — 80 metri quadri, tre locali, un bagno, ristrutturato, al secondo piano con ascensore — se si trovasse in ciascun quartiere. Fissando le caratteristiche dell'immobile, l'unica cosa che resta a variare è la posizione, e tutti i quartieri finiscono per essere misurati con lo stesso metro.

Il confronto fra le due letture cambia la classifica.

| quartiere | prezzo medio | stesso appartamento |
|---|---|---|
| Brera | € 12.303 | € 8.672 |
| Tre Torri | € 11.754 | € 7.796 |
| Duomo | € 11.080 | € 8.411 |
| Parco Bosco in Città | € 2.904 | € 3.736 |

Tre Torri perde quasi 4.000 euro al metro quadro e scende dal secondo al terzo posto, superata dal Duomo. Il suo prezzo medio molto elevato non dipende infatti dalla posizione quanto dal fatto che in quella zona gli appartamenti sono in media di 179 metri quadri e di costruzione recente. A parità di immobile, Tre Torri vale meno di quanto il prezzo medio lasci intendere.

Parco Bosco in Città si comporta in modo esattamente opposto e guadagna 832 euro al metro quadro. Il suo prezzo medio è basso perché in quella zona si vendono case grandi, che al metro quadro costano meno; a parità di immobile, il quartiere vale più di quanto sembri.

Nessuna delle due letture è quella "giusta", perché rispondono a due domande diverse: quanto costano le case in un quartiere, e quanto vale abitare in quel quartiere.

### Una combinazione che a Milano non esiste

La visualizzazione tridimensionale mostra due variabili contemporaneamente: l'altezza dei blocchi rappresenta il prezzo, mentre il colore rappresenta la dimensione media degli appartamenti. Questo permette di individuare quali combinazioni delle due variabili esistano realmente in città.

Le zone con case grandi ed economiche esistono, e si trovano tutte in periferia. Esistono anche le zone con case grandi e costose, e corrispondono al centro. Non esiste invece nessuna zona con case piccole e costose: a Milano non si paga il metro quadro caro per stare stretti, lo si paga per stare in centro, dove peraltro le case sono anche grandi.

---

## Quanto ci si può fidare di questi numeri

Un'analisi seria dichiara i propri limiti con la stessa precisione con cui espone i risultati. Questi sono i limiti di cui tenere conto leggendo tutto quanto precede.

I prezzi analizzati sono quelli richiesti negli annunci e non quelli effettivamente pagati. A Milano lo scarto fra richiesta e rogito è reale e, cosa più importante, non è uniforme fra le zone: non si tratta quindi di un errore che si annulla quando si confrontano quartieri diversi.

I dati sono la fotografia di un singolo giorno, il 26 agosto 2026, e non una serie storica: nessuno dei risultati riguarda l'evoluzione dei prezzi nel tempo né consente previsioni. Va inoltre tenuto presente che gli annunci fotografano l'offerta ancora invenduta in quel momento, il che tende a sovrarappresentare gli immobili rimasti a lungo sul mercato rispetto a quelli venduti rapidamente.

Nulla di quanto riportato descrive un rapporto di causa ed effetto. Quando si legge che l'ascensore vale un 8,2 per cento in più, non si deve intendere che installarne uno faccia aumentare il prezzo di una casa di quella percentuale. Il significato corretto è che le case dotate di ascensore costano in media l'8,2 per cento in più di case per il resto simili — e chi ha l'ascensore possiede anche, sistematicamente, un edificio di un certo tipo e di una certa epoca. La distinzione non è una formalità.

Il modello è stimato su 14.639 annunci dei 16.346 disponibili, perché il 10,4 per cento presenta campi incompleti. Chi ha i campi incompleti non costituisce un campione casuale degli annunci, e questo introduce una possibile distorsione di cui non è possibile misurare l'entità.

La stima di quanto costerebbe lo stesso appartamento in ciascun quartiere è, appunto, una stima, e si appoggia tanto più al modello quanto più quel tipo di casa è raro in quella zona. Nel quartiere tipico il 44 per cento degli annunci è vicino all'appartamento di riferimento, il che rende la stima ben ancorata ai dati reali. Fa eccezione Tre Torri, dove la quota scende al 10 per cento: lì il numero va letto sapendo che il modello sta estrapolando più di quanto stia leggendo i dati di quella zona.

Restano infine alcune assunzioni tecniche del modello che i dati violano. Sono dichiarate apertamente nel [README](README.md), insieme alle contromisure adottate e alla verifica — condotta esplicitamente — che le conclusioni non cambiano.

---

## Come è stato realizzato il lavoro

L'analisi si articola in dieci fasi, che vanno dalla statistica descrittiva alla regressione lineare multipla fino alla costruzione della mappa, ed è interamente contenuta in un unico script Python, `milano_analysis.py`, che può essere rieseguito da capo per riprodurre ogni numero citato in questo documento.

Il dataset di partenza, estratto il 26 agosto 2026, conteneva 18.017 righe, ridotte a 16.346 dalla fase di pulizia. Le 1.671 righe scartate comprendono annunci di progetti multi-unità che ripetevano lo stesso prezzo decine di volte, immobili non residenziali e casi già segnalati come anomali dalla fonte stessa.

Ogni decisione presa durante la pulizia è documentata con il conteggio delle righe prima e dopo, comprese le operazioni che si sono rivelate inutili una volta eseguite. Il dettaglio completo, insieme alla discussione dei metodi statistici impiegati in ciascuna fase, si trova nel [README](README.md).
