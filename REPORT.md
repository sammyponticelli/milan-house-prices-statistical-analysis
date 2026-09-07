# What houses cost in Milan, and why

> 🇮🇹 Versione italiana: **[REPORT.it.md](REPORT.it.md)**

This document sums up the results of a statistical analysis of 16,346 property listings in Milan, pulled from the portal immobiliare.it on **26 August 2026**. The starting question is a simple one: what determines the price of a house in Milan, and how much does each factor weigh against the others?

The text is written to be read without any background in statistics. Anyone wanting the detail of the methods, the checks and the code will find it in the [README](README.md), which walks through all ten phases of the work.

Two things need saying before we start. The prices analysed are those **asked by sellers in the listings**, not those actually paid at completion. And they are a snapshot taken on a single day, 26 August 2026, rather than a time series: nothing written here concerns the movement of prices over time, nor allows it to be predicted.

---

## The main findings

The analysis reaches six conclusions, which the sections below explain one at a time.

Floor area is the factor that weighs more than any other, but its effect is not proportional: large homes cost more than proportionally more than small ones. The neighbourhood, on its own, explains more than half of the differences in price per square metre between one listing and another, which makes it the second most important factor. It is precisely for this reason that much of what looks like "luxury" value turns out to be the value of the address: once the neighbourhood is accounted for, the luxury premium halves.

There are then two negative results, that is, two things one would expect to matter which do not. The number of rooms has no effect on price once floor area and neighbourhood are known, and the same goes for the type of heating.

Finally, two observations about the geography of the city. Milan is not split between a centre and a periphery: moving from the cheapest zone to the dearest one, the climb is continuous, without jumps. And the average price of a zone is not a clean piece of information, because it mixes what the location is worth with what the properties standing on it are worth; separating the two changes the ranking of neighbourhoods.

---

## The market from above

The starting point is understanding how prices are distributed, because that determines which summary figure it makes sense to use.

| | mean | median |
|---|---|---|
| price | € 570,105 | € 379,000 |
| floor area | 95 m² | 80 m² |
| price per m² | € 5,622 | € 5,073 |

The distance between the two columns is not an accounting detail but the first result of the analysis. The median is the value that splits the listings exactly in half: half the homes for sale in Milan cost less than 379,000 euros. The mean, on the other hand, is 570,105 euros, almost fifty per cent higher, and the reason is that a minority of very expensive properties drags it upwards.

Just how narrow that minority is can be seen by looking at the two ends of the distribution. The dearest ten per cent of listings starts at 1.09 million euros, while the dearest one per cent starts at 3.5 million: between these two rungs there are almost two and a half million euros. The top end of the Milan market is, in short, a segment of its own with its own dynamics, and every time someone quotes "the average price in Milan" they are using a figure that this segment has shifted considerably.

For this reason the analysis works almost throughout in terms of price per square metre rather than absolute price. Dividing price by floor area removes the most obvious variable — large homes cost more, which is no discovery — and lets everything else come through. The effect of that division is measurable: the variability of prices falls by more than half. Put another way, much of the reason two homes have different prices is simply that one is bigger than the other.

---

## What determines the price

To answer the opening question, a statistical model was built that considers all the characteristics of a property at once, rather than examining them one at a time. The difference between the two approaches is substantial, and it is worth showing with a concrete example.

Looking at the raw data, homes with a lift cost on average 1,121 euros per square metre more than those without one. It would be wrong to conclude that the lift is worth that figure, because homes with a lift are typically in more recent buildings and in more central areas, and differ from the others in many respects at once. The right question is: what is a lift worth between two homes identical in every other way?

The model answers exactly that question, because it estimates the effect of each characteristic while holding all the others fixed. The result is that, for the same zone, floor area, condition and everything else, a lift is worth a price increase of 8.2 per cent. The rest of the difference observed in the raw data was not the lift: it was the neighbourhood and the kind of building the lift stands in.

Applying the same reasoning to every available characteristic gives the picture below, ordered from the most influential factor to the least.

| characteristic | effect on price, all else equal |
|---|---|
| floor area | every +1% of floor area corresponds to +0.80% of price |
| luxury segment | +44% |
| one more bathroom | +9.3% |
| one step up the condition scale | +8.4% |
| presence of a lift | +8.2% |
| each floor higher up | +1.2% |
| number of rooms | no detectable effect |
| type of heating | no detectable effect |

Taken together, the model explains 91 per cent of the differences in price between one listing and another. That is a very solid result, and it means that floor area, zone and a handful of property characteristics are almost entirely enough to determine what a home costs in Milan: the room left for unobserved factors is small.

### The two counter-intuitive results

The first concerns the number of rooms, which does not influence price in any appreciable way. For the same floor area, number of bathrooms and neighbourhood, having three rooms rather than two does not change what the home costs. This is not a result left uncertain for want of data: the model establishes that the true effect lies between −0.9% and +0.5%, ruling it out in both directions. What you pay for is the square metres, not the way they are divided up.

There is also an explanation for why, before the neighbourhood was taken into account, the number of rooms did appear to matter. Flats carved into many small rooms are characteristic of certain areas of the city, so the room count was acting as an indirect indicator of location rather than as a characteristic with a value of its own. Once location enters the model explicitly, that information becomes redundant.

The second result concerns the floor and is the opposite case. Without accounting for the zone, the floor appeared to matter almost not at all; once the control for neighbourhood was introduced, its effect quadrupled. The reason is that tall buildings are found both in the most expensive neighbourhoods and in the social-housing outskirts, and the two groups cancelled each other out, masking the real effect. It is a case in which looking at the data more carefully does not shrink an effect but brings it out.

---

## The weight of the address

If there is one result the analysis establishes without any ambiguity, it is how much location matters.

Comparing the 32 macro-zones into which the city is divided, it turns out that zone membership alone explains 55.6 per cent of the variability in price per square metre. It is worth pausing on what that means: having already removed floor area from the picture — because we are working per square metre — more than half of what distinguishes one listing from another is pure geography.

The gap between the extremes is a factor of 3.6, running from the 3,216 euros per square metre of the Bisceglie, Baggio and Olmi zone to the 11,481 euros of the Centro.

It would be a mistake, though, to conclude that the city is split into two blocks. Lining up all 32 zones from cheapest to dearest produces a continuous climb in which no jump appears to separate a "centre" from a "periphery". On price per square metre, Milan is a gradient.

That gradient does, however, have an asymmetric shape. The first dozen zones are packed into a very narrow band, between 3,200 and 4,500 euros per square metre: twelve different zones separated by barely 1,300 euros in total. The last four, by contrast, cover almost 2,000 euros on their own. At the bottom of the ranking the neighbourhoods resemble one another to the point that it is often impossible to tell them apart statistically; at the top they pull away quickly.

There is finally a third aspect, less immediate but no less solid: the dearer a zone is, the more unpredictable it is internally. In outlying areas prices are compressed into a narrow band, whereas in the centre that same band is about five times wider. Buying in the centre means not only paying more, but entering a market in which the prices of two apparently similar properties can diverge considerably.

### Half of the "luxury" value is really the address

The most instructive result emerges from comparing the same model estimated twice, once without and once with the information about the neighbourhood.

| | without neighbourhood information | with neighbourhood information |
|---|---|---|
| luxury segment premium | +97% | +44% |
| lift premium | +12.7% | +8.2% |

The premium attached to the luxury segment halves. What appeared in the first model as the value of a prestige property was, for more than half, simply the value of the neighbourhood it stands in. The same mechanism, to a lesser degree, applies to the lift.

---

## The map

The final output of the work is an interactive map of the city, in the file `milano-3d.html`, which opens with a double click in any browser and works without an internet connection. The city is divided into the 88 official zones of the Municipality of Milan, known as NIL, or *Nuclei d'Identità Locale*.

Each zone is drawn as a block whose height corresponds to the price. The map can be viewed in three dimensions or flat, and hovering over a zone shows its exact figures.

The map covers 16,333 of the 16,346 available listings and represents 78 of the 88 zones. The ten excluded zones deserve an explanation: nine have fewer than ten listings each and one, Stephenson, has none at all. They are left grey rather than coloured, because a price computed from four properties is not comparable with one computed from eight hundred, and colouring them the same way as the others would make what is little more than an impression look like a measurement.

### Why a zone's average price is ambiguous

The most interesting part of the map arises from a problem of interpretation.

The average price of a neighbourhood mixes two distinct pieces of information: what it is worth to be in that part of the city, and what the homes located there are like. The two are not independent, because in the more expensive zones the homes are also on average larger and better renovated. As a result, the average price makes those zones look even dearer than location alone would justify.

To separate the two effects, the map offers a second reading: what the same identical flat — 80 square metres, three rooms, one bathroom, renovated, on the second floor with a lift — would cost in each neighbourhood. By fixing the characteristics of the property, the only thing left to vary is the location, and every neighbourhood ends up measured with the same yardstick.

Comparing the two readings changes the ranking.

| neighbourhood | mean price | same flat |
|---|---|---|
| Brera | € 12,303 | € 8,672 |
| Tre Torri | € 11,754 | € 7,796 |
| Duomo | € 11,080 | € 8,411 |
| Parco Bosco in Città | € 2,904 | € 3,736 |

Tre Torri loses almost 4,000 euros per square metre and drops from second to third place, overtaken by Duomo. Its very high average price depends not so much on location as on the fact that flats there average 179 square metres and are of recent construction. For a like-for-like property, Tre Torri is worth less than its average price suggests.

Parco Bosco in Città behaves in exactly the opposite way and gains 832 euros per square metre. Its average price is low because large houses are sold there, and large houses cost less per square metre; for a like-for-like property, the neighbourhood is worth more than it seems.

Neither reading is the "right" one, because they answer two different questions: what homes cost in a neighbourhood, and what it is worth to live in that neighbourhood.

### A combination that does not exist in Milan

The three-dimensional view shows two variables at once: the height of the blocks represents the price, while the colour represents the average size of the flats. This makes it possible to see which combinations of the two variables actually occur in the city.

Zones with large, cheap homes exist, and they are all on the outskirts. Zones with large, expensive homes also exist, and they are the centre. What does not exist is any zone with small, expensive homes: in Milan you do not pay a high price per square metre in order to be cramped, you pay it to be in the centre, where the homes happen to be large as well.

---

## How far these figures can be trusted

A serious analysis states its limits with the same precision it uses for its results. These are the limits to bear in mind when reading everything above.

The prices analysed are those asked in the listings, not those actually paid. In Milan the gap between asking price and completion price is real and, more importantly, it is not uniform across zones: this is therefore not an error that cancels out when different neighbourhoods are compared.

The data are a snapshot of a single day, 26 August 2026, and not a time series: none of the results concerns how prices evolve, nor supports any forecast. It is also worth keeping in mind that listings capture the supply still unsold at that moment, which tends to over-represent properties that have sat on the market a long time relative to those that sold quickly.

Nothing reported here describes a cause-and-effect relationship. When you read that a lift is worth 8.2 per cent more, it does not mean that installing one would raise a home's price by that percentage. The correct meaning is that homes with a lift cost on average 8.2 per cent more than otherwise similar homes — and a property with a lift also has, systematically, a building of a certain kind and a certain age. The distinction is not a formality.

The model is estimated on 14,639 of the 16,346 available listings, because 10.4 per cent have incomplete fields. Those with incomplete fields are not a random sample of the listings, and this introduces a possible bias whose size cannot be measured.

The estimate of what the same flat would cost in each neighbourhood is, precisely, an estimate, and it leans on the model the more that type of home is rare in that zone. In the typical neighbourhood 44 per cent of listings are close to the reference flat, which anchors the estimate firmly to real data. The exception is Tre Torri, where the share falls to 10 per cent: there the figure should be read knowing that the model is extrapolating more than it is reading that zone's own data.

Some technical assumptions of the model are, finally, violated by the data. They are stated openly in the [README](README.md), together with the countermeasures adopted and the explicit check that the conclusions do not change.

---

## How the work was carried out

The analysis is organised into ten phases, running from descriptive statistics through multiple linear regression to the construction of the map, and is contained entirely in a single Python script, `milano_analysis.py`, which can be re-run from scratch to reproduce every figure quoted in this document.

The starting dataset, extracted on 26 August 2026, contained 18,017 rows, reduced to 16,346 by the cleaning phase. The 1,671 rows discarded include listings for multi-unit developments that repeated the same price dozens of times, non-residential properties, and cases already flagged as anomalous by the source itself.

Every decision taken during cleaning is documented with the row count before and after, including the operations that turned out to be unnecessary once carried out. The full detail, together with a discussion of the statistical methods used in each phase, is in the [README](README.md).
