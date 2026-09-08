# Milan Real Estate — Statistical Analysis

> 🇮🇹 Versione italiana: **[README.it.md](README.it.md)**

> 🗺️ **[Explore the interactive 3D map →](https://sammyponticelli.github.io/milan-house-prices-statistical-analysis/milano-3d.html)** — runs in the browser, nothing to download.

**Which factors drive house prices in Milan, and what can statistical analysis tell us about the property market?**

The analysis works on ~18k sale listings collected from immobiliare.it and walks through the whole statistical toolkit — from descriptive statistics to multiple linear regression — to arrive at an **interactive map of price by zone**, in [`milano-3d.html`](https://sammyponticelli.github.io/milan-house-prices-statistical-analysis/milano-3d.html).

The write-up of the results, in a form readable without any background in statistics, is in **[REPORT.md](REPORT.md)**. This file documents the data, the method and the technical decisions.

---

## Dataset

`immobiliare_milano_vendita.csv` — **18,017 rows × 31 columns**, residential sale listings in Milan.

**Extraction date: 26 August 2026.** The date cannot be derived from the CSV, which has no time columns; the source is the `fonte_prezzi` field of the GeoJSON, which reads `Immobiliare.it, estrazione 2026-08-26`, consistent both with the file's modification time and with the first commit of the repository. The whole project is therefore a cross-section referring to a single day: no time-series analysis is possible, and none is attempted.

### Variables used in the analysis

| Variable | Type | Description |
|---|---|---|
| `price` | float | Asking price in € (50 missing) |
| `surface_mq` | float | Floor area in m² (29 missing) |
| `price_per_mq` | float | `price / surface_mq`, already computed in the file (79 missing) |
| `rooms` | string | Number of rooms — `1`…`5`, `5+`, plus ranges such as `2 - 4` for multi-unit developments |
| `bedrooms` | float | Number of bedrooms (2,014 missing) |
| `bathrooms` | string | `1`, `2`, `3`, `3+` (1,100 missing) |
| `floor` | string | Free text — `3`, `3 piano`, `piano terra`, `piano rialzato`, … (233 distinct values) |
| `elevator` | float | **Only `1.0` or missing** — no explicit `0` exists |
| `condition` | string | `Nuovo / In costruzione`, `Ottimo / Ristrutturato`, `Buono / Abitabile`, `Da ristrutturare` |
| `heating` | string | `Centralizzato`, `Autonomo`, `Assente` |
| `is_new` | int | New-build flag (419 listings) |
| `luxury` | int | Luxury segment flag (3,591 listings) |
| `typology` | string | `Bilocale`, `Trilocale`, `Appartamento`, `Attico`, `Loft`, … |
| `microzone` | string | Fine-grained zone, **144 distinct** (e.g. `Dergano`, `Maggiolina`) |
| `macrozone` | string | Aggregated zone, **32 distinct** (e.g. `Affori, Bovisa`) — the grouping variable of phases 4-5 |
| `nil_id`, `nil` | float / string | Zone of belonging, **88 distinct** — the join key of the phase 10 map, whose ids match those of the GeoJSON exactly |
| `lat`, `lon`, `has_geo` | float / int | Coordinates; 16,727 listings are geocoded — used for the zone centres on the map |

### Variables not used in the statistical analysis

| Variable | Description |
|---|---|
| `id`, `unit` | Listing identifier and sub-unit index (see below) |
| `url`, `title`, `address` | Free text / identifiers |
| `city`, `region` | Constants (`Milano` / `Lombardia`) |
| `category` | `Residenziale` (16,469), `Nuove costruzioni` (137), `Palazzi - Edifici` (135) — used as a **filter**, not as a variable |
| `agency` | Selling agency (569 missing) — a possible extension, outside the main model |
| `is_outlier`, `price_is_range` | Quality flags already present in the source — used as **filters** |

---

## Data cleaning

**Phase complete.** Cleaning came down to five decisions, all taken before computing any statistic. Each is implemented in `milano_analysis.py` as a function of its own, and every step prints the row count before and after, so that the cascade of filters remains inspectable rather than merely asserted.

**1. Remove sub-units.** Multi-unit listings, that is new-build developments, appear in the file as a parent row with `unit = 0` followed by one row per flat with `unit = 1, 2, 3…`, and all these rows repeat the very same `price`: in one case there are thirty-six sub-units for a single price. The filter `unit == 0` removes 1,276 of them, taking the dataset from 18,017 to 16,741 rows. It should be said that sub-unit rows have no `category` value, so the next filter would remove them anyway; the explicit filter on `unit` is kept because it keeps the intent visible in the code, rather than entrusting it to a side effect of another step.

**2. Apply the source's quality flags.** There are three filters and they are applied in cascade; it is the cascade, more than the individual filters, that reveals something about the data.

| Filter | Rows left | Removed |
|---|---|---|
| after `unit == 0` | 16,741 | — |
| `category == 'Residenziale'` | 16,469 | 272 (`Nuove costruzioni` 137, `Palazzi - Edifici` 135) |
| `is_outlier == 0` | 16,346 | 123 |
| `price_is_range == 0` | 16,346 | **0** |

In the raw file these flags mark 1,567 outliers and 1,321 range prices, but almost all of those rows have already been removed by the preceding filters. Listings with a range price are, by construction, the multi-unit developments, and after the first two filters not a single one survives. The `price_is_range` filter placed downstream therefore discards nothing, and remains in the code as an explicit check rather than an active step. It is a case in which the expected result, roughly 1,300 rows to discard, and the actual one, zero, diverge completely: the explanation of the divergence is worth more than the figure itself.

**3. Discard rows without a price or a floor area.** The three variables `price`, `surface_mq` and `price_per_mq` are the ones everything else in the analysis depends on. In the raw file they are missing in 50, 29 and 79 rows respectively, but after the quality filters the missing values are zero for all three, because here too the gaps were concentrated in rows already removed. The step therefore reduced to a confirmation check.

**4. The `elevator` column, where a missing value means "no".** In the raw file this column takes only two values, `1.0` in 13,572 rows and `NaN` in the remaining 4,445, with no explicit zero ever appearing. This is not a column with gaps in it, but a presence-only encoding: the field is written only when the listing declares a lift. It is therefore recoded into a clean 0/1 dummy, which on the filtered dataset counts 12,367 properties with a lift and 3,979 without.

The alternative, that is treating the `NaN` values as genuinely missing data, would automatically exclude 4,445 listings, 27% of the dataset, from the phase 8 regression. It would moreover be anything but a random exclusion, because listings with an empty field are systematically older, smaller and more peripheral properties, precisely the segment needed to estimate the effect of a lift. One would lose the data and at the same time introduce a bias, instead of avoiding one.

The residual risk of the chosen encoding is that some property really does have a lift without the field having been filled in. Those cases end up labelled as "without" and have the effect of attenuating β₅ towards zero, which means the estimated effect comes out smaller than the truth and never larger. It is therefore a conservative error, and phase 8 estimates β₅ = 0.0789 knowing it is, if anything, an underestimate. An empirical check of this assumption is not possible, for a reason explained in phase 8 which itself follows from the presence-only encoding.

**5. Convert the text columns into numeric ones.** Three columns arrive from the source as strings and need translating into numbers.

- `rooms` — `5+` → 5 (609 rows); ranges such as `2 - 4` are discarded by regex, but **none remain** on the filtered dataset, since they appeared only on the multi-unit rows already removed at step 1. No rows are lost here.
- `bathrooms` — `3+` → 3 (313 rows).
- `floor` — lower-cased, then `piano terra` → 0 (2,035 rows) and `piano rialzato` → 0.5 (1,267 rows); for the rest the first number is extracted, so `3 piano` → 3.

The overall result of the cleaning is 16,346 usable listings, 90.7% of the raw file, of which 16,333 have a zone of belonging. All 32 macro-zones survive the filters with at least 115 listings each, which is enough for the between-group comparisons of phases 4 and 5 without having to merge categories. No duplicate rows are found.

### Residual missing values on the clean dataset

The three load-bearing variables are complete, while what remains uncovered concerns the peripheral variables. These missing values are handled at modelling time rather than upstream, because dropping the incomplete rows now would mean losing them for all the analyses that do not use those variables.

| Variable | Missing | Share | Note |
|---|---|---|---|
| `bathrooms` | 844 | 5.2% | relevant to phase 8 |
| `condition` | 587 | 3.6% | likewise |
| `floor` | 544 | 3.3% | text not reducible to a number |
| `bedrooms` | 444 | 2.7% | outside the main model |
| `rooms` | 106 | 0.6% | |
| `lat` / `lon` / `nil` | 13 | 0.1% | excluded from the phase 10 map |
| `microzone` | 57 | 0.3% | `macrozone` is missing in only 12 |

The phase 8 regression uses `rooms`, `bathrooms`, `condition` and `floor` at once, and the cumulative loss from dropping incomplete rows came to 1,707 rows, 10.4% of the total: the full model therefore runs on 14,639 listings. The missing values of the different columns overlap only partly, which explains why the total cost is lower than the sum of the individual shares but higher than the largest of them.

One anomaly is finally worth watching: the `floor` column contains a value of 41 in a single row. A forty-first floor is implausible in Milan, so the case should be inspected before phase 7, where residuals become the object of analysis. The other extreme values, 19 and 21, are compatible with the towers of Porta Nuova and CityLife.

---

## Structure of the analysis

### Phase 1 — Descriptive Statistics

**Phase complete.** The `descriptive_statistics` function computes mean, median, mode, variance, standard deviation, minimum, maximum, quartiles, interquartile range, range, coefficient of variation and skewness on the three central variables — `price`, `surface_mq` and `price_per_mq` — and collects them into a single table. Alongside it, `plot_boxplots` produces a box plot for each of the three, which makes visible the same asymmetry the numbers declare: the upper whisker is very long, and beyond the third quartile a dense cloud of points builds up.

The point of the phase, however, does not lie in the individual numbers but in the comparison between the three variables.

| | mean | median | CV | skewness |
|---|---|---|---|---|
| `price` | € 570,105 | € 379,000 | **1.18** | 5.68 |
| `surface_mq` | 95 m² | 80 m² | 0.67 | 3.42 |
| `price_per_mq` | € 5,622 | € 5,073 | **0.47** | 1.83 |

There are two things to read in this table. The first is that the mean clearly exceeds the median for all three variables, which indicates right-skewed distributions and leads to an operational conclusion: the mean is not a good summary of the typical Milan listing, because a handful of properties above ten million euros drags it upwards by about half.

The second is that the coefficient of variation falls from 1.18 to 0.47 as soon as price is normalised by floor area. This means that much of the raw variability in prices is simply variability in the size of the properties. It is the first substantive result of the project, and it is also the reason why `price_per_mq` becomes the comparison variable from phase 4 onwards.

### Phase 2 — Probability & Distributions

**Phase complete.** The phase is organised into five steps, all carried out on the same three central variables.

- **Histograms** (`plot_hist`), with mean and median marked by two vertical lines on the chart, so that the asymmetry is seen rather than deduced from the phase 1 table.
- **Q-Q plots** against the normal (`plot_qq`, via `scipy.stats.probplot`). The right tail departs sharply from the diagonal: it is the same asymmetry as before, read on the quantiles.
- **Percentiles** p1, p5, p10, p25, p50, p75, p90, p95, p99 (`percentile_statistics`) — on a distribution like this one, a table of percentiles says far more than a mean.
- **Shape statistics** (`distribution_shape`): kurtosis alongside skewness, in a single table.
- **Log transformation** of `price` (`log_transform`), with the two scales shown side by side — histogram and fitted normal curve on the raw price on the left, on `log(price)` on the right (`plot_log_comparison`). The normal curve overlaid on the histograms of the three variables in their original scale is in `plot_normal_distribution`.

**Percentiles**

| | p1 | p10 | p25 | p50 | p75 | p90 | p99 |
|---|---|---|---|---|---|---|---|
| `price` (€) | 85,950 | 190,800 | 260,000 | 379,000 | 600,000 | 1,090,000 | 3,511,000 |
| `surface_mq` (m²) | 25 | 45 | 56 | 80 | 110 | 160 | 360 |
| `price_per_mq` (€/m²) | 1,576 | 3,045 | 3,941 | 5,073 | 6,695 | 8,762 | 15,399 |

The jump from the ninetieth to the ninety-ninth percentile of price is worth almost two and a half million euros. The dearest ten per cent of the market is, in short, a world apart, and on its own explains why the mean measured in phase 1 sits at 570,105 euros against a median of 379,000. On price per square metre the same distance compresses considerably, going from 8,762 to 15,399 euros, that is less than double: normalising by floor area removes size from the picture and leaves only the premium for location and quality in play.

**Shape of the distribution**

| | skewness | excess kurtosis |
|---|---|---|
| `price` | 5.68 | **54.98** |
| `surface_mq` | 3.42 | 19.79 |
| `price_per_mq` | 1.83 | 5.88 |

Kurtosis adds information that skewness alone does not provide. A value of 54.98 against the zero of the normal distribution indicates enormously heavier tails, which means that extreme events are nowhere near as rare as a normal with the same mean and standard deviation would predict. The normal curve overlaid on the histogram makes this obvious at a glance: the Gaussian fitted on the mean and sigma of price turns out to be too wide in the middle and too thin in the tails. It is not slightly off, it has the wrong shape.

**Log transformation**

Applying the logarithm to price brings skewness down from 5.68 to 0.66 and kurtosis from 54.98 to 1.34. The result is not a normal distribution, which no real data ever is, but it is close enough to symmetry to make the parametric apparatus used in phases 4 to 8 defensible, and it constitutes the empirical justification for the log-log specification adopted in phase 7. On price per square metre the logarithm works even better, taking skewness to −0.07.

A note on method closes the phase. With 16,346 observations, formal normality tests such as Shapiro-Wilk or D'Agostino reject the null hypothesis on any real dataset, because their power to detect even a wholly irrelevant departure is effectively one. For this reason the phase relies on Q-Q plots and shape statistics rather than on tests, and states the reason for that choice explicitly instead of simply omitting them.

### Phase 3 — Sampling & Confidence Intervals

**Phase complete.** The design of this phase consists in treating the 16,346 clean listings as if they were the entire population, whose true parameters are therefore known, and in drawing samples from it. In this way the estimate obtained from each sample and the real value are genuinely comparable, something that almost never happens in statistical practice. All the calculations are carried out on `price_per_mq`.

- **Population parameters** (`population_parameters`): μ = **€ 5,621.55**/m², σ = **€ 2,644.29**/m². σ is computed with `ddof=0` — this is a population, not a sample, and the right denominator is N.
- **Distribution of the sample mean** (`draw_sample`): 1,000 samples without replacement for each sample size n = 30, 100, 500, with a histogram of the 1,000 means for each n.
- **Empirical against theoretical standard error**, in the same function: the standard deviation of the 1,000 means compared with σ/√n.
- **95% confidence intervals** using the *t* distribution and a **coverage check** (`confidence_intervals`): for each n, 1,000 intervals are built — each from its own sample mean and sample standard deviation, as anyone holding a single sample would do — and it is counted how many actually contain μ.

**The central limit theorem in practice**

| n | empirical SE | theoretical σ/√n |
|---|---|---|
| 30 | € 482.82 | € 482.78 |
| 100 | € 262.73 | € 264.43 |
| 500 | € 120.82 | € 118.26 |

The two columns agree to within a few euros, and for n = 30 the first three digits are identical. Going from n = 100 to n = 500 the dispersion shrinks by exactly the factor of root five predicted by theory, and this happens on a population with skewness 1.83, where the individual observation is not remotely normally distributed. The histogram of the sample means, by contrast, is symmetric and bell-shaped already at n = 30: here the central limit theorem is seen at work rather than merely cited.

A more exact benchmark would in fact exist. Since the samples are drawn without replacement from a finite population, the correct formula would be sigma over root n multiplied by the finite population correction factor, which at n = 500 would take the theoretical value from 118.26 to 116.40 euros. The correction turns out to be negligible, because n stays small relative to a population of 16,346 units, and the comparison is left on the standard formula because that is the one the phase means to discuss.

**Coverage of the intervals**

| n | observed coverage |
|---|---|
| 30 | **94.2%** |
| 100 | **93.8%** |
| 500 | **94.5%** |

All three coverages sit below the nominal 95%, but reading this table correctly requires knowing how large its margin of error is. Each coverage is itself an estimate, obtained from a thousand repetitions, and its Monte Carlo error is worth about seven tenths of a point. The three figures are therefore compatible both with one another and with 95%, which means that not much can be concluded from this single run, and least of all that n = 100 covers worse than n = 30, which is what the table would appear to suggest.

The real pattern only becomes visible by repeating the whole experiment. Across **six independent series** of 1,000 intervals each, the mean coverage comes out as:

| n | mean of 6 series | observed range |
|---|---|---|
| 30 | **93.53%** | 93.0 – 93.9 |
| 100 | 94.50% | 93.8 – 95.9 |
| 500 | 95.17% | 94.5 – 96.2 |

With six series the picture becomes readable. At n = 30 all six fall between 93.0 and 93.9 without ever approaching 95%, which indicates systematic under-coverage; the standard deviation across series, at 0.35 points, is too small for this to be noise. At n = 500, by contrast, the mean climbs back to 95.17%, that is exactly the nominal value. An order of magnitude more repetitions is therefore needed for what a single table cannot show to emerge from the noise. The explanation of the phenomenon is the expected one: the interval built on the t distribution assumes a normal population, whereas here skewness is 1.83 and at n = 30 the central limit theorem has not yet finished its work, so the interval delivers less than it promises. It remains, though, an explanation that the initial single table is not enough to demonstrate.

This is the methodological result of the phase, and it is worth more than a tidy table of coverages: the confidence level is a property of the procedure under its assumptions, and measuring it requires, in turn, enough data to tell signal from noise. Taking the repetitions from a thousand to ten thousand would reduce the margin of error to two tenths of a point and would make the table readable for what it appears to say.

A note on reproducibility. The functions `draw_sample` and `confidence_intervals` each construct a `np.random.default_rng(42)` generator and pass it to every call of `.sample(...)`, so that two consecutive runs produce output identical line by line, which has been verified. It is essential that the generator be created once outside the loop and left to advance: passing `random_state=42` directly to `.sample()` would produce a thousand copies of the same sample, not a thousand reproducible samples.

### Phase 4 — Hypothesis Testing

**Phase complete.** The phase carries out four formal two-sample comparisons on `price_per_mq`, all two-tailed and with the significance level set at 0.05.

The whole apparatus of the test is gathered into a single reusable function, `two_sample_test(group_1, group_2)`, which returns Levene's test, Welch's t-test, the degrees of freedom, the 95% confidence interval for the difference between the means and Cohen's d. The `hypothesis_testing` function merely extracts the groups and calls it four times, so that the statistical logic is written and verified once while the comparisons remain simple data. The Welch–Satterthwaite degrees of freedom and the confidence interval are computed explicitly from the formula rather than read off a ready-made output, because in this phase building the test by hand is precisely the point of the exercise.

**Test 1 — two zones.**

> **H₀**: μ(zone A) = μ(zone B) — the mean price per m² is the same in the two zones
> **H₁**: μ(zone A) ≠ μ(zone B) — two-tailed

The two pairs were chosen deliberately for contrast. The first compares zones that are very far apart, where the outcome of the test is a foregone conclusion and the genuinely interesting quantity is the size of the effect. The second compares `Ripamonti, Vigentino` with `Porta Vittoria, Lodi`, two zones whose centres are 2.4 kilometres apart and which have almost identical sample sizes: it is here that the test does real work.

| | `Centro` vs `Bisceglie, Baggio, Olmi` | `Ripamonti, Vigentino` vs `Porta Vittoria, Lodi` |
|---|---|---|
| n | 389 vs 426 | 511 vs 518 |
| mean €/m² | 11,812 vs 3,301 | 4,953 vs 5,164 |
| difference | **+8,511** | **−211** |
| t (Welch) | 38.90 | −2.26 |
| degrees of freedom | 428.8 | 1,023.4 |
| p | 9.6 × 10⁻¹⁴³ | **0.024** |
| 95% CI of the difference | [8,081; 8,941] | **[−393; −28]** |
| Cohen's d | **2.84** | **−0.14** |
| Levene (p) | 5.7 × 10⁻⁶⁴ | 0.324 |

The two columns formally lead to the same conclusion, the rejection of the null hypothesis, and they mean nothing alike.

In the left-hand column Cohen's d is 2.84, which means the two distributions are separated by almost three standard deviations. In a situation like that the p-value is a figure devoid of informative content, and the quantity that really matters is the confidence interval, which places the gap between 8,081 and 8,941 euros per square metre.

In the right-hand column sits the didactic result of the phase. The p-value of 0.024 leads to rejecting the null hypothesis at the 5% level, but Cohen's d is −0.14, which by Cohen's own conventions is a negligible effect, given that the threshold for calling it even small is 0.2. Above all, the confidence interval runs from −393 to −28 euros per square metre, which places its upper end just 28 euros from zero. Translated onto an 80 m² flat, the true gap between the two zones could be worth 31,000 euros or 2,200: the test has established that the two zones are not identical, and nothing else. This is exactly why the effect size and the confidence interval appear next to every p-value, and it is not an abstract warning: with around 500 observations per group, a difference of four per cent is enough to clear the significance threshold.

**Test 2 — a property characteristic.** The same apparatus is then applied to `elevator` and to `condition`, to show that hypothesis testing does not concern geography alone.

| | `elevator` yes vs no | `Da ristrutturare` vs `Ottimo / Ristrutturato` |
|---|---|---|
| n | 12,367 vs 3,979 | 1,560 vs 7,004 |
| mean €/m² | 5,894 vs 4,773 | 5,160 vs 6,145 |
| difference | **+1,121** | **−984** |
| t (Welch) | 26.13 | −14.28 |
| degrees of freedom | 8,072.5 | 2,554.0 |
| p | 1.6 × 10⁻¹⁴⁴ | 1.5 × 10⁻⁴⁴ |
| 95% CI of the difference | [1,037; 1,205] | [−1,120; −849] |
| Cohen's d | 0.43 | −0.37 |
| Levene (p) | 4.8 × 10⁻¹⁹ | 1.1 × 10⁻⁴ |

Both effects come out clearly significant and of medium size, with d at 0.43 and −0.37, an order of magnitude above that of the pair of nearby zones. These are, however, raw differences computed without any control: lifts are more common in recent and central buildings, and properties in need of renovation are systematically larger and older. How much of those 1,121 euros per square metre really belongs to the lift, rather than to the zone or the type of building the lift stands in, is a question the t-test cannot even pose. The multiple regression of phase 8 is needed, where the same variables re-enter controlled for zone and floor area, and the comparison between the coefficient estimated there and the raw difference reported here is one of the expected results of phase 9.

It is worth explaining the choice between Levene and Welch. Levene's test rejects the homogeneity of variances in three cases out of four, and it does so spectacularly in the comparison between `Centro` and the outskirts, where the standard deviations are 4,206 against 1,009 and the two zones do not even share an order of magnitude of dispersion. Only for the pair of nearby zones does the test fail to reject, with p at 0.324.

Despite this, Welch's test is used in all four comparisons. The reason is simple: when the variances really are homogeneous Welch coincides in practice with Student, as can be seen from the fact that in the nearby pair the degrees of freedom fall to 1,023.4 against Student's 1,027, an irrelevant difference; when they are not, Student is wrong. A test that costs nothing in the favourable case and saves the day in the unfavourable one does not need to be chosen case by case. Note by contrast the collapse of the degrees of freedom in the first comparison, down to 428.8 against Student's 813: it is Welch discounting the disproportionate variance of `Centro`.

The phase finally discusses the type I error, that is the rejection of a true null hypothesis, which corresponds to the five per cent of cases accepted by fixing the significance level; the type II error; and the reason why a large sample size makes statistically significant differences that are minuscule and of no practical relevance. This last point, in this phase, is not a theoretical hypothesis but a measured result, and it is the right-hand column of the first table.

### Phase 5 — ANOVA

**Phase complete.** The ANOVA is the natural extension of phase 4 to all 32 macro-zones considered together, and is carried out on 16,334 listings, since the 12 lacking a `macrozone` value exclude themselves. The phase consists of five functions orchestrated by `anova_phase`: `anova_analysis`, `welch_anova`, `residual_diagnostics`, `tukey_posthoc` and `plot_macrozone_boxplots`.

> **H₀**: μ₁ = μ₂ = … = μ₃₂ — the mean price per m² is the same in every zone of Milan
> **H₁**: at least one zone differs

**One-way ANOVA** (`anova_analysis`)

| | |
|---|---|
| F | **658.07** |
| degrees of freedom | 31; 16,302 |
| p | < 10⁻³⁰⁰ (returned as 0.0) |
| η² | **0.556** |

The null hypothesis is rejected without room for discussion, but here too the p-value is the least interesting part of the result: with over sixteen thousand observations and a ratio of 3.6 between the dearest and the cheapest zone, no other outcome was conceivable. The quantity that carries information is eta squared, at 0.556, which means that zone membership alone explains 55.6% of the variance in price per square metre. More than half of what distinguishes one listing from another, once floor area has been removed from the picture, is therefore geography: it is the figure that justifies both the zone dummies of phase 8 and the entire deliverable of phase 10. Eta squared too is computed by hand, as the ratio of between-group to total sum of squares, rather than taken from a ready-made output.

**Checking the assumptions** (`welch_anova`, `residual_diagnostics`)

Levene's test returns a statistic of 89.40 with p effectively zero, which indicates that the homogeneity of variances is violated grossly. This was already foreshadowed by the per-zone standard deviations, which run from the 826 euros of Forlanini to the 4,206 of Centro, a factor of five. Hence the decision to add Welch's ANOVA, which does not assume homogeneity: it returns F = 451.70 with degrees of freedom 31 and 4,249.0 and p still effectively zero. The two F statistics are not comparable with each other as numbers, because Welch penalises the denominator degrees of freedom heavily, taking them from 16,302 to 4,249, but the conclusion does not move a millimetre. It is the case in which it is best to state that the assumption is violated and that the result holds anyway, instead of having to choose between the two statements.

The chart `charts/anova_residuals.png` shows the phenomenon visually. Since the fitted values are only 32, that is the group means, the residuals arrange themselves into 32 vertical stripes, and these stripes widen progressively from left to right: around 4,000 euros per square metre the residuals stay within five thousand euros, while around 12,000 they approach fifteen thousand. Expensive zones, in other words, are not only dearer but also internally less homogeneous. The Q-Q plot of the residuals then confirms the heavy right tail already known from phase 2, which means that the normality of the residuals is violated as well; with 16,334 observations, however, the central limit theorem makes this second violation of little consequence for the F test, unlike heteroskedasticity.

**Post-hoc: Tukey HSD** (`tukey_posthoc`)

Of the 496 possible pairs, 426 come out significant, that is 86%, and 70 do not. Correcting for multiple comparisons is mandatory here: 496 independent t-tests carried out at the 5% level would by construction produce about 25 false positives, a number equal to more than a third of the 70 pairs that remain non-significant here.

The effect of the correction is best seen on a case already known — the pair of nearby zones from phase 4:

| | phase 4 (Welch, uncorrected) | phase 5 (Tukey, corrected) |
|---|---|---|
| `Ripamonti, Vigentino` vs `Porta Vittoria, Lodi` | p = **0.024** → reject | p-adj = **0.992** → do not reject |

The difference is the same, 211 euros per square metre, the data are the same, and the conclusion is the opposite. In phase 4 that comparison was the only place being looked at, whereas here it is one of 496 possible ones, and the confidence level is recalibrated accordingly: the Tukey interval widens to [−626; +205] and ends up including zero. It is not that one of the two tests is wrong, they simply answer two different questions, and the distance between those two questions is precisely the multiple comparisons problem.

The pairs with the widest gap are all comparisons between `Centro`, or `Bisceglie, Baggio, Olmi`, and the rest of the city; the largest is the one between those two zones, at 8,511 euros per square metre, the same already measured in phase 4. At the opposite end, the smallest difference that survives the correction is worth 360 euros per square metre and concerns `Famagosta, Barona` against `Uptown, Cascina Merlata, Viale Certosa`, with adjusted p of 0.027. Below that threshold, at these sample sizes, Tukey's test no longer distinguishes.

**Box plots by macro-zone** (`plot_macrozone_boxplots`). The chart `charts/macrozone_boxplots.png` arranges the 32 zones in order of increasing median. It is the visual counterpart of the test, and shows three things the F statistic does not.

The first is that the climb is continuous: from the median of 3,216 euros of `Bisceglie, Baggio, Olmi` up to the 11,481 of `Centro` no jump appears, no threshold separating a centre from a periphery. On price per square metre, Milan is a gradient and not two distinct markets.

The second is that the first dozen zones nonetheless form a plateau: from `Bisceglie` through to `Udine, Lambrate` the medians all sit between 3,200 and 4,500 euros, that is twelve different zones packed into barely 1,300 euros, while the last four cover almost two thousand on their own. This is why Tukey's 70 non-significant pairs are concentrated almost entirely at the bottom of the ranking: there the zones really are close to one another.

The third is that the width of the boxes grows along with the median: the interquartile range of `Bisceglie` fits within a thousand euros, while that of `Centro` exceeds five thousand. It is the same heteroskedasticity already seen in the residual chart, observed from another angle, and it has a concrete reading: buying in the centre means not only paying more, but entering a considerably less predictable market.

### Phase 6 — Correlation

**Phase complete.** The phase measures the bivariate relationships with `price`, and does so by computing each relationship twice, with Pearson and with Spearman. There are four functions, gathered under `correlation_phase`: `prepare_correlation_data` encodes `condition` on an ordinal scale from 1 to 4, `correlation_analysis` computes the two coefficients with their p-values, `correlation_matrix` produces a heatmap over all pairs of variables and `pearson_spearman_comparison` a side-by-side bar chart.

| variable | Pearson | Spearman | gap | n |
|---|---|---|---|---|
| `surface_mq` | **0.789** | 0.763 | −0.026 | 16,346 |
| `bathrooms` | 0.623 | 0.646 | +0.023 | 15,502 |
| `rooms` | 0.547 | **0.646** | **+0.100** | 16,240 |
| `floor` | 0.136 | 0.167 | +0.031 | 15,802 |
| `condition_numeric` | **0.051** | 0.115 | +0.064 | 15,759 |

All the coefficients come out significant, with p below 10⁻¹⁰, and for the first three variables the p-value even underflows and is printed as zero. But with around sixteen thousand observations significance distinguishes nothing, exactly as was already the case in phase 4. What does distinguish is the magnitude of the coefficients, and above all the gap between the two columns.

**Where Pearson and Spearman diverge, and why**

The most interesting case is that of `rooms`, where the two coefficients are 0.547 and 0.646, ten points apart. The cause lies in the data and not in the statistics: the variable is truncated from above, because the source's `5+` value was mapped to 5, so that a ten-room penthouse and a large four-room flat end up sharing the same value. Pearson, which works on the values, is penalised both by this artificial ceiling and by the tails of price, whereas Spearman, which works on ranks, is far less affected. The true relationship between number of rooms and price is therefore stronger than Pearson declares, and the only way to notice is to compute both.

Floor area goes in the opposite direction, at 0.789 against 0.763, and is the only case in which Pearson exceeds Spearman. The relationship between price and floor area is genuinely close to linear on the values, and the large luxury properties, which sit in the tail of both variables, reinforce Pearson while in a ranking they would count no more than any other observation. It is the bivariate confirmation of what phase 7 goes on to model.

The negative result of the phase concerns `condition`, and it is more informative than many positive ones: Pearson's coefficient is 0.051, that is a practically null correlation between state of repair and price. This does not mean that renovating does not pay, but that the ordinal scale from 1 to 4 fails to capture the relationship. In the dataset, properties marked `Da ristrutturare` are systematically larger, averaging 107.6 m² against the 90.9 of those in `Ottimo / Ristrutturato` condition, and are concentrated in the historic districts: the penalty for condition and the premium for size and location cancel each other out, and almost nothing is left on the total price. Phase 4, which compared the same two categories on price per square metre rather than on absolute price, had instead found a clear difference of 984 euros per square metre with d of −0.37. Same variable, two different measures, two opposite answers: it is a textbook case of why the dependent variable must be chosen before interpreting the coefficient.

**Multicollinearity, ahead of phase 8**

The heatmap in `charts/correlation_matrix.png` covers all pairs of variables, but the block that really matters is not the price row, it is the triangle of correlations among the predictors.

| | `surface_mq` | `rooms` | `bathrooms` |
|---|---|---|---|
| `surface_mq` | 1 | **0.751** | **0.726** |
| `rooms` | 0.751 | 1 | **0.710** |
| `bathrooms` | 0.726 | 0.710 | 1 |

Three variables correlated with one another between 0.71 and 0.75 are largely measuring the same thing, namely how big the property is. This is the multicollinearity problem of phase 8 becoming visible for the first time, and it is why that phase computes VIFs rather than putting all three variables into the model and trusting to luck. It is also worth noting that `rooms` correlates with `surface_mq` at 0.751, that is more strongly than it correlates with `price`, where it stops at 0.547: the number of rooms says more about the floor area than about the price.

The variables `condition_numeric` and `floor` are by contrast uncorrelated with everything else, with correlations no greater than 0.14 in absolute value, which makes them harmless in the multiple model: they do not explain much, but they do not disturb any other predictor.

The phase produces two charts. The first, `charts/correlation_matrix.png`, is an annotated heatmap with a diverging palette centred on zero, chosen so that the warm block of the size predictors stands out at a glance from the neutral band of `condition` and `floor`. The second, `charts/pearson_spearman_comparison.png`, places the bars of the two measures side by side for each variable: the gap for `rooms` is by far the most evident, and it is also the chart that makes visible how `rooms` and `bathrooms`, though far apart on Pearson, arrive at the identical rank correlation of 0.646.

That correlation does not imply causation is a principle that here finds a concrete example rather than a slogan. The variable `bathrooms` correlates with price at 0.62, but adding a second bathroom to a flat in Quarto Oggiaro certainly does not bring it closer to Brera. The number of bathrooms is simply an indicator of the presence of large, central and expensive properties, and it is no accident that it correlates with floor area at 0.726, almost as strongly as it correlates with price. The confounding factor is size and, above all, location, which phase 5 has just established explains 55.6% of the variance in price per square metre on its own. It is exactly for this reason that phase 8 introduces a control for the zone.

### Phase 7 — Linear Regression

**Phase complete.** The phase estimates two different specifications on all 16,346 listings. The variables `price` and `surface_mq` are complete, and the positivity filter required by the logarithm discards nothing, since the minimum values are 20,240 euros and 15 square metres. There are seven functions, gathered under `linear_regression_phase`: three for the simple model and three for the log-log one, each trio made up of estimation, residual diagnostics and the Breusch-Pagan test.

**Specification 1 — linear** (`linear_regression`)

```
Price = −215,563 + 8,274 · Surface
```

| | |
|---|---|
| β₁ | **8,273.86** €/m² |
| 95% CI of β₁ | [8,174.99; 8,372.73] |
| t | 164.03 |
| p | < 10⁻³⁰⁰ (printed as 0.0) |
| R² | **0.622** |

Every additional square metre brings 8,274 euros of price with it, and floor area alone explains 62.2% of the variance. The coefficient must, however, be read for what it is: the marginal square metre costs 8,274 euros, while the average square metre of the dataset costs 5,622, as measured in phase 1. This is not a contradiction but the same thing said twice, namely that price per square metre grows with the size of the property; the log-log specification discussed below quantifies it precisely.

The intercept, at −215,563 euros, has no sensible interpretation, because it corresponds to the price the model would assign to a property of zero square metres. The smallest observed is 15 square metres, so zero lies far away from any real data and the intercept is merely the point at which the line crosses an axis that describes no existing property. It is the classic coefficient one reports without interpreting.

**The diagnostics fail the model** (`linear_residual_diagnostics`, `breusch_pagan_test`)

The Breusch-Pagan test returns an LM statistic of 2,743.0 with p effectively zero, and the chart `charts/linear_regression_residuals.png` shows why in the most didactic form possible. The residuals fan out perfectly: around fitted values of 200,000 euros they stay within a few tens of thousands of euros, while beyond four million they reach six million in either direction. The variance of the error is therefore not constant, and the homoskedasticity assumption on which OLS rests is violated blatantly. The Q-Q plot of the residuals adds a second violation, with the classic S shape signalling tails much heavier than a normal's.

The consequences are precise and worth spelling out. The coefficient β₁ = 8,274 remains correct, because heteroskedasticity does not bias the OLS point estimate, but its standard error does not: consequently the confidence interval [8,175; 8,373] and the t statistic of 164 are unreliable. This is precisely why phase 8 turns to HC3 robust standard errors.

**Specification 2 — log-log** (`log_linear_regression`)

```
log(Price) = 8.136 + 1.0913 · log(Surface)
```

| | |
|---|---|
| β₁ (elasticity) | **1.0913** |
| 95% CI of β₁ | **[1.0786; 1.1041]** |
| t | 167.84 |
| R² | 0.633 |
| Breusch-Pagan | LM = **179.8**, p = 5.3 × 10⁻⁴¹ |

In this specification β₁ is an elasticity, which means that a 1% increase in floor area corresponds to a 1.09% increase in price. The interesting value is not 1.09 in itself, however, but its comparison with unity: if price were proportional to floor area, that is if price per square metre were independent of size, the elasticity would be exactly 1. The confidence interval, running from 1.0786 to 1.1041, excludes unity by a wide margin. In Milan, therefore, large properties cost more than proportionally, and doubling the floor area more than doubles the price. It is the main result of the phase, and it coincides with the fact the linear specification expressed clumsily through a negative intercept.

**Why the log-log is preferred, and why not on R²**

The two R² values, 0.622 and 0.633, are not comparable with each other, because they measure the explained variance of two different dependent variables, `price` in the first case and `log(price)` in the second. Ranking them would be a mistake, and this is why the preference for one of the two specifications is not argued on that ground.

The preference is argued on the residuals instead. The Breusch-Pagan test still rejects, with p at 5 × 10⁻⁴¹, which means the log-log specification does not solve heteroskedasticity but reduces it. The LM statistic, however, falls from 2,743 to 180, that is by a factor of fifteen, and with 16,346 observations the test would reject any departure however minimal, as was already seen with the normality tests in phase 2. It is therefore the comparison between the two magnitudes that carries information, not the outcome of the test.

The chart then settles the matter without need of further statistics. In `charts/log_linear_regression_residuals.png` the fan has disappeared, the cloud of residuals has an almost constant width across the whole range of fitted values, and the Q-Q plot stays on the diagonal nearly everywhere, with a slight departure in the lower tail alone. Compared with the pronounced S of the linear model, this is another category of adherence to the assumptions.

The second specification is therefore the preferred one, and it is also the only one directly comparable with the full model of phase 8, which starts from here and adds further regressors.

**Chart of the fitted line.** The file `charts/linear_regression.png` shows the cloud of 16,346 points with the OLS line overlaid, in the original scale. The fan of residuals is already visible here, before turning to the dedicated chart.

### Phase 8 — Multiple Linear Regression

```
log(Price) = β₀ + β₁·log(Surface) + β₂·Rooms + β₃·Bathrooms + β₄·Condition
           + β₅·Elevator + β₆·Floor + β₇·Heating + β₈·Luxury + zone dummies + ε
```

**Phase complete.** The model is written in formula form through `sm.formula.ols`, so that the expressions `C(macrozone)` and `C(heating)` generate their own dummy variables: 31 for the macro-zones and 2 for heating, taking the first category in alphabetical order as the reference. The phase consists of seven functions gathered under `multiple_regression_phase`.

**The sample shrinks.** Since the regression requires all the variables at once, dropping incomplete rows costs 1,707 observations, taking the sample from 16,346 to 14,639 rows, that is 10.4% fewer. It is the cumulative price of the missing values scattered over `bathrooms`, `condition` and `floor`, at 5.2%, 3.6% and 3.3% respectively: the estimate announced in the cleaning section finds its actual measurement here. All the figures in this phase hold on those 14,639 rows, including the two specifications of the final comparison table, which were refitted on the same subset precisely so that AIC and R² come out comparable.

**Multicollinearity: nothing to remove** (`vif_analysis`)

| variable | VIF |
|---|---|
| `log_surface` | **4.67** |
| `rooms` | **4.17** |
| `bathrooms` | 2.54 |
| `luxury` | 1.26 |
| `elevator` | 1.11 |
| `floor` | 1.11 |
| `condition_numeric` | 1.06 |

The correlation among the three size predictors observed in phase 6, between 0.71 and 0.75, translates into VIFs of 4.67 and 4.17: high values, close to the conventional threshold of 5, but nonetheless below it. No variable is therefore removed, and the table serves to document a decision taken on the basis of the numbers rather than to justify one already taken. It is worth being explicit about what these values mean: a VIF of 4.67 indicates that the standard error of `log_surface` is about 2.2 times what it would be with uncorrelated predictors. Collinearity, in short, is not absent: it is knowingly tolerated.

**The full model** (`multiple_regression`)

| | coefficient | p |
|---|---|---|
| `log_surface` | **0.8019** | < 0.001 |
| `luxury` | **0.3642** | < 0.001 |
| `bathrooms` | 0.0893 | < 0.001 |
| `condition_numeric` | 0.0811 | < 0.001 |
| `elevator` | 0.0789 | < 0.001 |
| `floor` | 0.0121 | < 0.001 |
| `rooms` | −0.0018 | **0.593** |
| `heating` autonomous | −0.0035 | **0.779** |
| `heating` central | −0.0108 | **0.387** |

**R² = 0.9062 · adjusted R² = 0.9059 · AIC = −4,441**

The two R² values are barely three ten-thousandths apart despite the model using around forty regressors. With 14,639 observations the penalty introduced by the adjustment is minimal, and the comparison serves precisely to show that in this case the risk of overfitting does not materialise; with the same number of regressors and a few hundred observations it would have gone differently.

Since the dependent variable is logarithmic, the coefficients read as approximate percentage changes. One more bathroom is associated with a price 8.9% higher, a lift with 7.9%, one step up the `condition` scale with 8.1% and one floor higher with 1.2%. For the `luxury` flag the linear approximation no longer suffices and the exact conversion is required, which gives a premium of 44%.

It is worth noting that the elasticity of floor area falls from 1.09 to 0.80. In phase 7 `log_surface` was the only regressor and therefore absorbed everything correlated with the size of the property, whereas here `bathrooms` and `rooms` are part of the model and take a share of it. It is the same phenomenon already observed in phase 6, seen from the other side, and it is why the coefficient of a simple regression and that of a multiple one are not the same quantity: they answer different questions.

**What changes when the zone is controlled for** (`zone_comparison`)

The same model estimated twice, with and without the macro-zone dummies:

| | coef without zone | p without zone | coef with zone | p with zone |
|---|---|---|---|---|
| `log_surface` | 0.7813 | < 0.001 | 0.8019 | < 0.001 |
| `luxury` | **0.6791** | < 0.001 | **0.3642** | < 0.001 |
| `elevator` | **0.1196** | < 0.001 | **0.0789** | < 0.001 |
| `condition_numeric` | 0.0589 | < 0.001 | 0.0811 | < 0.001 |
| `bathrooms` | 0.0914 | < 0.001 | 0.0893 | < 0.001 |
| `floor` | 0.0027 | 0.008 | 0.0121 | < 0.001 |
| `rooms` | −0.0120 | **0.006** | −0.0018 | **0.593** |
| `heating` central | −0.0401 | **0.012** | −0.0108 | **0.387** |

The adjusted R² goes from 0.8458 without the zone dummies to 0.9059 with them: the macro-zone dummies alone therefore add six points of explained variance to a model that already explained 85%.

In the transition two predictors lose their significance, and it is the most instructive result of the phase.

- **`rooms`** goes from p = 0.006 to p = 0.593. For a given floor area, the number of rooms appeared to say something about price; once the neighbourhood is known it says nothing at all. It was acting as an indicator of location — flats carved into many small rooms are typical of certain areas — rather than as a characteristic with a value of its own.
- **`heating` central** goes from p = 0.012 to p = 0.387, for the same reason: central heating is a feature of apartment blocks of certain periods and certain neighbourhoods.

Two other coefficients shrink without losing significance: `luxury` almost halves, going from 0.679 to 0.364, and `elevator` falls by about a third, from 0.120 to 0.079. Half of the premium associated with luxury was, literally, the neighbourhood.

One coefficient finally moves in the opposite direction: `floor` quadruples, going from 0.0027 to 0.0121, and its p-value drops from 0.008 to below 0.001. Without the control for zone the effect of the floor was masked, because tall buildings are found both in the dearest neighbourhoods and in the social-housing outskirts and the two groups cancelled each other out. It is the case in which introducing a control does not shrink an effect but reveals it.

**Robust standard errors** (`robust_standard_errors`)

The same model is refitted with `cov_type='HC3'`. The standard errors rise, as was to be expected after the Breusch-Pagan test of phase 7: for `log_surface` they go from 0.0072 to 0.0091, an increase of 26%, and for the intercept from 0.0285 to 0.0385, an increase of 35%. The variables with strong coefficients do not shift by a comma in their conclusions, while the two `heating` categories, already non-significant, become even more so, with the p-value going from 0.779 to 0.841. No conclusion of the phase therefore depends on the choice between classical and robust standard errors, and this is exactly the information the analysis needed to produce: not that HC3 is better in the abstract, but that here it does not change the answer.

**Residuals** (`multiple_residual_diagnostics`) — `charts/multiple_regression_residuals.png`

The cloud of residuals against fitted values has a substantially constant width from a log-price of 12 up to 15, with no trace of the fan seen in phase 7. The Q-Q plot stays on the diagonal throughout the central portion, with a departure in the left tail corresponding to a group of properties the model clearly overvalues, that is listings far cheaper than their characteristics and their zone would predict. These are a few dozen cases out of 14,639, which do not threaten the estimates, but they constitute the only residue of unexplained structure left.

**Model comparison** (`model_comparison`)

| model | adjusted R² | AIC |
|---|---|---|
| simple log-log | 0.6554 | 14,531.0 |
| full multiple | **0.9059** | **−4,441.2** |

Both models are estimated on the same 14,639 rows and on the same dependent variable `log_price`, which is the necessary condition for the comparison to make sense. It is also the reason why the linear model of phase 7 does not appear in the table: its dependent variable is `price`, and an AIC computed on a different scale would not be comparable. The jump is clear on both criteria, since explained variance goes from 66% to 91% and the roughly nineteen thousand fewer AIC points indicate that adding the regressors amply pays for the extra complexity.

**A promise the data do not allow us to keep.** Earlier versions of this README planned a sensitivity analysis on `elevator`, to be carried out by refitting the model on the subset of 13,572 rows with the field actually filled in. That test is not, however, executable: in the source the variable is either `1.0` or `NaN` and never `0`, so the subset with the field filled in contains exclusively properties equipped with a lift. In the absence of variation the coefficient is not identifiable and the variable would simply be dropped from the estimation. The reasoning about the encoding remains valid, because misclassification can only attenuate β towards zero and therefore 0.0789 is if anything an underestimate, but it is an argument and not an empirical check, and it is declared here as such.

### Phase 9 — Statistical Conclusions

**Phase complete.** The phase produces no new estimate: it reuses the model already fitted in phase 8, which `multiple_regression_phase` returns together with the data frame, and derives from it the table on which the conclusions are written. There are three functions: `conclusions_table` builds coefficients, 95% confidence intervals, p-values and significance flags; the split between significant and non-significant predictors happens inside `conclusions_phase`; and `zone_variance_share` quantifies the contribution of the zone.

**The predictors, with their confidence intervals**

| predictor | β | 95% CI | significant at α = 0.05 |
|---|---|---|---|
| `log_surface` | **0.8019** | [0.7878; 0.8160] | ✅ |
| `luxury` | **0.3642** | [0.3526; 0.3757] | ✅ |
| `bathrooms` | 0.0893 | [0.0806; 0.0980] | ✅ |
| `condition_numeric` | 0.0811 | [0.0769; 0.0853] | ✅ |
| `elevator` | 0.0789 | [0.0699; 0.0878] | ✅ |
| `floor` | 0.0121 | [0.0105; 0.0137] | ✅ |
| `rooms` | −0.0018 | [−0.0086; 0.0049] | ❌ |
| `heating` autonomous | −0.0035 | [−0.0283; 0.0212] | ❌ |
| `heating` central | −0.0108 | [−0.0353; 0.0137] | ❌ |

Six predictors out of nine come out significant. The way this phase reports results, however, runs through confidence intervals rather than p-values, because the interval says how large the effect is and with what precision, whereas the p-value merely says whether the effect is distinguishable from zero. It is the same distinction phase 4 had already insisted on when discussing the pair of nearby zones.

**The conclusions, in the form in which they should be written**

> **Floor area** shows a positive and statistically significant relationship with price (β = 0.802, 95% CI [0.788; 0.816], p < 0.001). After controlling for the other characteristics of the property **and for the zone**, it remains by far the strongest predictor: a 1% increase in floor area is associated with a **0.80%** increase in price, all else equal.

> The **luxury** flag is associated with a price **44% higher** (β = 0.364, 95% CI [0.353; 0.376], p < 0.001) than a property with the same characteristics in the same zone. Without the zone control the same coefficient was 0.679, that is a premium of 97%: **more than half of what looks like a luxury premium is in fact the neighbourhood**.

> An additional **bathroom** is associated with a price **9.3% higher** (β = 0.089, 95% CI [0.081; 0.098], p < 0.001), one step up the **state of repair** scale with **8.4%** (β = 0.081, 95% CI [0.077; 0.085]), the presence of a **lift** with **8.2%** (β = 0.079, 95% CI [0.070; 0.088]) and each **floor** higher up with **1.2%** (β = 0.012, 95% CI [0.011; 0.014]). The percentages are e^β − 1; for floor area, which enters in logarithms, β is directly an elasticity and the conversion does not apply.

> The **number of rooms** shows no significant association with price once floor area, bathrooms and zone are controlled for (β = −0.002, 95% CI [−0.009; 0.005], p = 0.593). The same holds for the **type of heating** (p = 0.779 and p = 0.387). In the case of rooms the conclusion is stronger than a simple "not significant": the confidence interval places the true effect between **−0.9% and +0.5%**, ruling it out in both directions. This is not ignorance about the effect, it is the finding that the effect is negligible.

**How much location weighs** (`zone_variance_share`)

| | adjusted R² |
|---|---|
| model without zone dummies | 0.8458 |
| model with zone dummies | 0.9059 |
| **difference** | **+0.0602** |

The zone dummies add six points of explained variance to a model that already explained 84.6%. The figure should be read together with the one from phase 5, where the macro-zone alone explained 55.6% of the variance in price per square metre: the two results do not contradict each other, they answer two different questions. To the question of how much location explains taken on its own, the answer is a great deal; to the question of how much it adds for someone who already knows the floor area, bathrooms, condition and floor of the property, the answer is six points. The reason is that part of the geographic information is already contained in the characteristics of the properties themselves, since the large, renovated ones are distributed anything but uniformly across the city.

**The limits, stated without hedging**

- These are **asking prices**, not transaction prices. In Milan the gap between asking price and completion is real and is not constant across zones, so it is not even an error that cancels out in comparisons.
- The listings are a **snapshot**. Nothing asserted here concerns a movement over time, and the coefficients say nothing about how prices will move.
- Everything is **associative**. No causal claim is made, and none is obtainable from this design: β = 0.079 on the lift does not mean that installing one raises the price by 8.2%, but that properties with a lift cost on average 8.2% more than otherwise similar properties. The difference is not a formality — a property with a lift also has, systematically, a building of a certain kind.
- The model runs on **14,639 listings out of 16,346**: 10.4% are excluded by listwise deletion, and those with incomplete fields are not a random sample of the listings.
- Some **assumptions remain violated but declared**: heteroskedasticity is reduced and not eliminated (hence the HC3 errors), and the residuals have a heavy left tail.

### Phase 10 — Map of price by zone

**Phase complete.** The final deliverable: **`milano-3d.html`**, an interactive map of the 88 NIL of Milan (*Nuclei d'Identità Locale*, the official city zones), in two views and with two price variables. Nine functions orchestrated by `map_phase`. `milano-heatmap.html` remains in the repository as the reference map the work started from: it is not an output of this phase and its aggregates are not the ones computed here.

**Point-in-polygon was not needed.** The original plan was to assign each listing to a zone by geometric intersection, since the 144 microzones and 32 macro-zones present in the CSV do not coincide with the 88 NIL. The CSV, however, already carries a `nil_id` column, and the compatibility check came out clean: 88 identifiers in common with the GeoJSON and zero mismatched names. The assignment therefore reduces to a `groupby('nil_id')`, without needing to add `shapely` or `geopandas` to the dependencies. The row of the dataset table declaring `nil_id` unused has been corrected accordingly.

| | |
|---|---|
| listings with a zone | **16,333** out of 16,346 (13 without coordinates) |
| zones with at least one listing | 87 out of 88 — Stephenson has none |
| zones represented | **78** |
| zones suppressed | **9**, with 1 to 9 listings each |

**Suppressing the small zones.** Colouring a zone means asserting something about its price, and a mean built on four observations is not comparable with one built on 834. The threshold was set at ten listings: below it, the block stays grey and flat and the tooltip reads "not enough data" rather than a number. This is not a neutral choice, and it is the one point of the phase left open: nine zones of the city say nothing, and the decision between giving them a value by shrinking it towards the city mean, lowering the threshold or merging them with neighbouring zones has not yet been taken.

**Mean or median?** The original request concerned the mean price per square metre, so it is the mean that governs the height of the blocks. The median does not disappear from the map, though: it appears in the tooltip together with the interquartile range, and that is where the asymmetry established in phase 1 can be read. The gap between the two measures is informative in itself: it averages one and a half percentage points, but in one zone it reaches 35%, and a wide gap signals a zone with a few very expensive properties rather than a uniformly expensive zone.

#### The two price variables

The first variable, the **mean price**, is the one actually asked in the zone. It has the drawback of conflating two distinct pieces of information: what the location is worth and what the properties standing on it are worth. Phase 6 already hinted at this, since the correlation between mean price and mean floor area by zone is 0.572.

The second variable, the **reference flat**, separates the two. It is obtained by refitting the phase 8 model with NIL dummies rather than macro-zone ones, and then using it to price a single identical flat in each zone.

| | |
|---|---|
| rows | 14,591 |
| zones estimated | **77** |
| adjusted R² | **0.9215** (against 0.9059 with the macro-zones) |
| reference flat | 80 m², 3 rooms, 1 bathroom, renovated, floor 2, lift, central heating |
| range of values | from € 2,630 to € 8,672 /m² |

The two measures correlate at 0.98, but the distances change, and that is exactly where the useful information lies:

| zone | mean price | reference flat | gap |
|---|---|---|---|
| Brera | 12,303 | **8,672** | −3,631 |
| Tre Torri | 11,754 | **7,796** | −3,958 |
| Duomo | 11,080 | **8,411** | −2,669 |
| Parco Bosco in Città | 2,904 | **3,736** | **+832** |

Tre Torri loses almost 4,000 euros per square metre and drops from second to third place, overtaken by Duomo: its raw price is inflated by the fact that flats in that zone average 179 square metres and are of recent construction, not by the location itself. At the opposite end Parco Bosco in Città gains ground, because the raw price understates it: large houses are sold there, and they cost less per square metre. It is the quantified answer to the question phase 9 raised without closing, namely that more than half of what looks like a luxury premium is in fact the neighbourhood.

**The limit of this variable, measured.** The most obvious objection is that no real listing coincides with the reference flat. It is the same objection one could raise against price per square metre, and the answer is the same: the construction serves to compare zones on equal terms. It remains true, however, that the estimate leans on the model the further a zone is from the reference, and this distance can be measured. The share of listings between 60 and 100 square metres is 44% in the median zone, and only two zones out of 78 fall below 15%: Parco Sempione at 9% and Tre Torri at 10%. Since Parco Sempione is already excluded from the model for insufficient sample size, a single zone remains, Tre Torri, in which the figure is more an extrapolation of the model than a reading of that zone's data, and it should be read knowing this.

#### The two views

In the **3D** view height and colour carry two different variables: height represents price and colour the mean floor area, split into five quantile classes with cuts at 81, 88, 94 and 107 square metres. It is therefore a bivariate map, able to show something a single-variable map could not: where the expensive small flats are and where the cheap large ones are. The result is that the first case does not exist at all, because no zone combines small flats with high prices. In Milan you do not pay a high price per square metre in order to be cramped.

In the **2D flat** view, with the height gone, it is the colour that takes on the price, again in five quantile classes recomputed on each of the two price variables. It is a less striking and more precise representation, because no zone can hide another.

In both views the classes are defined by quantile rather than by equal intervals, because on a skewed distribution equal intervals would produce four almost empty classes and one containing everything else.

| variable | cuts of the 5 classes |
|---|---|
| mean floor area (m²) | 81 · 88 · 94 · 107 |
| mean price (€/m²) | 3,498 · 4,280 · 5,114 · 7,019 |
| reference flat (€/m²) | 3,648 · 4,208 · 4,809 · 5,910 |

#### The representation choices, and why

Height always starts from zero. Subtracting the minimum to make the differences stand out would make a zone at 6,000 euros per square metre look twice as expensive as one at 5,000, which would be a misleading representation. The scale factor is 0.3 and is stated in the legend: the dearest zone thus stands about 3.7 kilometres tall on a city eighteen wide.

Height seen in perspective is not, however, a reliable measuring scale. A distant block looks lower than a nearby one of the same height, tall blocks hide the ones behind them, and the area of the polygon, which means nothing, ends up carrying visual weight. Three countermeasures follow from this awareness: a text ranking of all the zones, where comparisons can actually be read; the tooltip with the exact figures; and the 2D view, which removes the problem at the root.

Selecting a zone, either from the ranking or by clicking it directly on the map, drops the others to a third of their height and fades them, turns the map automatically to the side with the least tall mass in front of the chosen zone, and shows a label with its name and value. This is a temporary focus state, in which the selected zone keeps its true height. To go back to the overview it is enough to click away from the zones or press Esc.

The ground is dark in both views. The first attempt was made on a light ground with white edges between the blocks, but the edges turned out to be invisible and the blocks ended up merging into one another. Both colour ramps are sequential and single-hue, orange for floor area and blue for price, and run from light to dark as the value grows, with every step checked for a contrast of at least 3:1 against the ground. This limit is real and constrained the choice: a step darker than `#a05520` on the orange, or `#256abf` on the blue, falls below the threshold and the top class starts to disappear into the background.

Zooming out is finally capped at level 10, just below that of the overview: with no street map underneath the zones, going wider would only shrink Milan inside an empty screen.

#### The file

The file `milano-3d.html` weighs 2.71 MB and is completely self-contained, because both the rendering library — deck.gl 9.4.0, in the file `deck.min.js`, with the version pinned exactly as for the Python dependencies — and the GeoJSON of the 88 zones are embedded in it. It makes no network requests and downloads no map tiles: it opens with a double click and works offline.

It is worth being clear about what the map is not. It is a coup d'œil and not a measuring instrument, a role filled by the ranking and the tooltip. All the limits declared in phase 9 also remain in force: these are asking rather than transaction prices, a snapshot rather than a trend, and associative rather than causal relationships.

---

## Progress

| Phase | Status |
|---|---|
| 0. Data cleaning | ✅ **complete** — 18,017 → 16,346 listings |
| 1. Descriptive Statistics | ✅ **complete** — statistics table + box plots |
| 2. Probability & Distributions | ✅ **complete** — histograms, Q-Q plots, percentiles, shape statistics, log |
| 3. Sampling & Confidence Intervals | ✅ **complete** — CLT verified, coverage measured |
| 4. Hypothesis Testing | ✅ **complete** — 4 Welch tests with effect sizes and CIs |
| 5. ANOVA | ✅ **complete** — η² = 0.556, Welch, Tukey, diagnostics |
| 6. Correlation | ✅ **complete** — Pearson vs Spearman, heatmap, multicollinearity |
| 7. Linear Regression | ✅ **complete** — simple and log-log, elasticity 1.09 |
| 8. Multiple Linear Regression | ✅ **complete** — adj. R² = 0.906, VIF, zone dummies, HC3 |
| 9. Statistical Conclusions | ✅ **complete** — effects, CIs, limits declared |
| 10. Map of price by zone | ✅ **complete** — interactive 3D/2D map, 78 zones, reference flat |

---

## Project structure

```
milano_real_estate_analysis/
├── milano_analysis.py                  # analysis script — cleaning + phases 1-10
├── immobiliare_milano_vendita.csv      # dataset (18,017 × 31)
├── milano_zone_NIL.geojson             # 88 NIL polygons — input of phase 10
├── milano-3d.html                      # interactive map — output of phase 10
├── deck.min.js                         # deck.gl 9.4.0, embedded in the map
├── milano-heatmap.html                 # the 2D reference map work started from
├── charts/                             # figures of phases 1-8 in PNG (14 files)
├── REPORT.md                           # write-up of the results, for anyone
├── REPORT.it.md                        # Italian version
├── README.it.md                        # Italian version
└── README.md
```

The dataset, the geometries and the rendering library are already in the project folder, so the analysis script can use relative paths and should be launched from that folder.

Every plotting function saves its PNG into `charts/` with `plt.savefig(..., dpi=150)` and only then displays it with `plt.show()` — in that order, because `show()` clears the figure and after it there would be nothing left to save. The files produced so far are `boxplots.png` (phase 1), `histograms.png`, `qq_plots.png`, `normal_distribution.png`, `log_comparison.png` (phase 2), `sampling_distributions.png` (phase 3), `anova_residuals.png` and `macrozone_boxplots.png` (phase 5), `correlation_matrix.png` and `pearson_spearman_comparison.png` (phase 6), `linear_regression.png`, `linear_regression_residuals.png` and `log_linear_regression_residuals.png` (phase 7), and `multiple_regression_residuals.png` (phase 8).

The pipeline, in the order in which it runs in `milano_analysis.py`:

```
# cleaning
inspect_data              → info, shape, describe, missing, duplicates on the raw file
inspect_categorical       → value_counts of the categorical variables
remove_subunits           → filter unit == 0                        18,017 → 16,741
inspect_quality_variables → check the flags before filtering
apply_quality_filters     → category / is_outlier / price_is_range  16,741 → 16,346
inspect_missing_values    → confirm: price, surface_mq, price_per_mq complete
encode_elevator           → NaN → 0, 0/1 dummy
inspect_text_variables    → actual shape of rooms, bathrooms, floor before parsing
parse_text_variables      → from string to numeric
validate_clean_data       → shape, missing, duplicates, dtypes, final distributions

# phase 1
descriptive_statistics    → table of 13 statistics × 3 variables
plot_boxplots             → box plots of price, surface_mq, price_per_mq

# phase 2
plot_hist                 → histograms with mean and median marked
plot_qq                   → Q-Q plots against the normal
percentile_statistics     → table of 9 percentiles × 3 variables
distribution_shape        → skewness and kurtosis × 3 variables
plot_normal_distribution  → density histograms + fitted normal curve
log_transform             → skewness and kurtosis of log(price)
plot_log_comparison       → price against log(price), side by side, with normal curve

# phase 3
population_parameters     → μ and σ (ddof=0) of price_per_mq on the population
draw_sample               → 1,000 samples for n = 30/100/500, histograms + empirical vs theoretical SE
confidence_intervals      → 1,000 95% t intervals for each n, coverage measured

# phase 4
two_sample_test           → helper: Levene, Welch, df, 95% CI of the difference, Cohen's d
hypothesis_testing        → the 4 comparisons (2 zone pairs, elevator, condition)

# phase 5 — orchestrated by anova_phase
anova_analysis            → F, degrees of freedom, p, η² computed from the sums of squares
welch_anova               → Levene over 32 groups + Welch's ANOVA
residual_diagnostics      → OLS price_per_mq ~ C(macrozone), residuals and Q-Q plot
tukey_posthoc             → Tukey HSD over 496 pairs, significant ones ordered by gap
plot_macrozone_boxplots   → box plots of the 32 zones ordered by median

# phase 6 — orchestrated by correlation_phase
prepare_correlation_data  → condition → ordinal scale 1-4 (condition_numeric)
correlation_analysis      → Pearson and Spearman with price, variable by variable
correlation_matrix        → 6 × 6 matrix + seaborn heatmap
pearson_spearman_comparison → side-by-side bars of the two measures

# phase 7 — orchestrated by linear_regression_phase
linear_regression         → OLS price ~ surface_mq: β, R², t, p, 95% CI
plot_linear_regression    → scatter with the fitted line
linear_residual_diagnostics → residuals vs fitted + Q-Q plot of the residuals
breusch_pagan_test        → LM, p, F on the linear model
log_linear_regression     → OLS log(price) ~ log(surface): elasticity
log_residual_diagnostics  → same diagnostics on the log-log model
log_breusch_pagan_test    → LM, p, F on the log-log model

# phase 8 — orchestrated by multiple_regression_phase
prepare_regression_data   → log_price, log_surface, dropna on the model variables
vif_analysis              → VIF of the seven numeric predictors
multiple_regression       → full model: R², adj. R², AIC, coefficients
zone_comparison           → same model with and without zone dummies, side by side
robust_standard_errors    → HC3 against classical standard errors
multiple_residual_diagnostics → residuals vs fitted + Q-Q plot
model_comparison          → simple log-log against full, on the same rows

# phase 9 — orchestrated by conclusions_phase
conclusions_table         → coefficients, 95% CIs, p-values, significance flags
zone_variance_share       → adj. R² with and without zone, and the difference

# phase 10 — orchestrated by map_phase
prepare_map_data          → only the listings with a nil_id        16,346 → 16,333
zone_aggregates           → n, mean, median, p25, p75, price and floor area per NIL
suppress_small_zones      → zones under 10 listings flagged, not coloured
location_premium          → OLS with NIL dummies, then the same flat priced in every zone
value_classes             → cuts of the 5 quantile classes, one set per variable
build_zone_geojson        → GeoJSON properties rewritten with our own aggregates
map_metadata              → summary, cuts, reference flat
write_3d_map              → deck.gl + GeoJSON embedded into milano-3d.html
```

Phase 8 returns `regression_data` together with the fitted model, which the main program passes on to phase 9: in this way the conclusions are read off the model already estimated rather than refitting it a second time.

Every transformation is preceded by its own inspection, on the principle of looking at how a column is made before modifying it. It is the reason it became clear in time that the second and third cleaning steps would turn out to be largely empty.

### Tools

`pandas` and `numpy` for the data work (`numpy` already in use for the log transformation of phase 2), `scipy.stats` for phases 2-6 (already in use for the Q-Q plots, for the normal curves overlaid on the histograms and for the *t* critical values of phase 3), `statsmodels` for phases 5, 7 and 8 — used through `statsmodels.api`, `anova_oneway`, `pairwise_tukeyhsd`, `het_breuschpagan` and `variance_inflation_factor` — `matplotlib` for the charts and `seaborn` for the phase 6 heatmap alone. Phase 10 adds no Python dependency — it uses `json` from the standard library — and entrusts the rendering of the map to **deck.gl 9.4.0**, embedded in the output file.

**Why statsmodels and not scikit-learn.** The project is an exercise in **statistical inference** — estimating population quantities from a sample and quantifying the uncertainty around them. Every phase from the third onwards needs standard errors, test statistics, p-values and confidence intervals, not just fitted values.

The two libraries estimate the same OLS model and return the same coefficients, but they are built for different questions:

| | `scikit-learn` | `statsmodels` |
|---|---|---|
| β coefficients, R² | ✅ | ✅ |
| Standard errors of β | ❌ | ✅ |
| t statistic and p-value per coefficient | ❌ | ✅ |
| Confidence interval for β | ❌ | ✅ |
| Adjusted R², AIC/BIC, F test on the model | ❌ | ✅ |
| Breusch-Pagan, Durbin-Watson, VIF, Tukey HSD | ❌ | ✅ |
| Robust standard errors (HC3) | ❌ | ✅ |
| Prediction on new data, cross-validation, regularisation | ✅ | limited |

scikit-learn is a **prediction** library: it optimises out-of-sample accuracy and deliberately leaves out the inferential apparatus, because for prediction the honest check is the error on unseen data, not a p-value. (A source of confusion: in the machine learning world "inference" means the opposite thing — running an already trained model to produce predictions.)

`sm.OLS(y, X).fit().summary()` prints in a single call the table of coefficients with standard errors, *t*, *p* and the 95% interval — and that table **is** the output of phases 7 and 8. A phase 9 sentence of the kind *"positive and statistically significant (β = …, p < 0.001) after controlling for the other characteristics"* is not something scikit-learn can produce.
