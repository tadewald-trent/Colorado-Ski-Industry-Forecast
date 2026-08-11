# RQ4 Synthesis: Does an ENSO forecast tell us anything useful about Colorado ski industry performance?

**Research question (from scoping.md):** Combining RQ1-RQ3: how much of
the variance in ski-industry revenue can plausibly be attributed to
weather vs. non-weather factors? What is the honest answer to "does
next winter's ENSO forecast tell us anything useful about ski industry
performance"?

This is the original motivating question that started this project.

## The causal chain, and where it breaks

The project was designed around a chain: **ENSO -> snowfall -> skier
visits -> revenue.** Each link was tested independently and honestly,
without assuming the next link would work just because a prior one did.

| Link | Question | Result | Strength |
|---|---|---|---|
| RQ1 | ENSO -> snowfall | No statistically significant relationship, in either region, across 8 separate tests (t-tests and regressions, 2 data sources) | Null - the chain breaks here |
| RQ2 | Snowfall -> visits | A real, directionally consistent relationship in the modern pass-pricing era, but not robust to removing a single extreme season | Suggestive, unconfirmed |
| RQ3 | Visits -> revenue | A statistically significant relationship that survived every sensitivity check applied | Robust - the strongest link in the chain |

**A chain is only as strong as its weakest link, and here the weakest
link is also the first one.** RQ3 shows visits reliably predict
revenue. RQ2 suggests, without confirming, that snow may predict
visits. But RQ1 found no detectable relationship at all between ENSO
and snowfall at these specific stations. Regardless of how strong the
downstream links are, a forecast that cannot reliably predict the first
link cannot be used to predict the last one through this pathway.

## Direct answer to the motivating question

**No. Based on this analysis, an ENSO/ONI forecast does not provide a
statistically supported basis for predicting Colorado ski industry
revenue or visitation.** This is not because the downstream business
relationships are weak, RQ3 in particular shows a real, robust link
between visits and revenue. It is because the first link in the chain,
the assumption that ENSO phase predicts snowfall at these specific
Colorado mountain stations, was not supported by the data, no matter
how it was tested.

This directly revisits the question that opened this project: whether
the forecast "Super El Niño" for winter 2026-27 says anything
meaningful about the upcoming ski season. **Based on this project's own
data and testing, rather than general literature, the honest answer
is: not with any statistical confidence.** A strong El Niño winter is
statistically indistinguishable, in this dataset, from any other ENSO
phase in terms of expected snowfall at these 7 stations.

## How much of revenue variance is weather vs. non-weather?

This project cannot give a precise variance decomposition (that would
require a full multi-factor regression model, a natural next step, not
attempted here), but the component findings support a qualitative
answer:

- **ENSO explains close to none of the variance in snowfall** (0.02% to
  0.53% r-squared across four regressions in RQ1).
- **Snowfall's relationship to visits, even where suggestive, explains
  at most a moderate share of visit variance, and only in a small,
  unconfirmed sample** (RQ2: 86.3% r-squared with all 7 modern-era
  seasons, dropping to a non-significant 60.8% with one season
  removed).
- **Visits explain a large, robust share of revenue variance**
  (RQ3: 75-78% r-squared, stable across three sensitivity checks).
- **Acquisitions and pricing, not tested quantitatively in this
  project, are known qualitatively to matter** (see the
  `is_acquisition_year` flag and the Epic/Ikon Pass launch history in
  `data_dictionary.md`), and RQ3 found that accounting for the one
  acquisition year in the sample did not meaningfully change the
  visits-revenue relationship, suggesting these may be additive rather
  than competing drivers.

Put simply: **the business side of this chain (visits -> revenue)
looks real and measurable. The climate side (ENSO -> snowfall) does
not, at least not at the station level tested here.**

## What this project demonstrates, beyond the specific answer

- **A stated hypothesis was tested rigorously and rejected when the
  data did not support it (RQ1)**, rather than reframed or downplayed.
- **A promising-looking result was stress-tested rather than accepted
  at face value (RQ2)**, and reported as unconfirmed once it failed
  that test.
- **A robust result was independently corroborated across multiple,
  meaningfully different checks (RQ3)**, giving real confidence in that
  one finding despite its small sample size.
- **A real data-quality issue (the CSCUSA measurement-basis
  discontinuity) was caught, documented, and correctly excluded from
  quantitative analysis**, rather than silently distorting results.
- **The overall conclusion is more useful, not less, for being
  negative on the headline question.** Knowing that ENSO forecasts do
  not reliably predict Colorado ski season outcomes is itself
  actionable information for anyone (a resort operator, an investor, a
  ski journalist) who might otherwise put weight on a seasonal ENSO
  outlook when planning for a specific Colorado market.

## Limitations of the project as a whole

- All findings are specific to the 7 core stations (and Vail Resorts
  as the single company case study) chosen for this project. They do
  not necessarily generalize to all of Colorado, to other ski
  companies, or to other mountain ranges.
- Sample sizes shrink sharply moving down the causal chain: hundreds of
  station-winters for RQ1, a dozen or fewer seasons for RQ2 and RQ3.
  The weakest statistical power is concentrated exactly where the
  business questions are most interesting.
- This project tested same-season relationships only (see the
  multi-year lag discussion considered but not implemented). A lagged
  or cumulative-drought-effect model was not tested and could reveal
  different patterns.
- No multi-factor model (controlling for multiple predictors
  simultaneously, e.g., snow, pricing, and macroeconomic conditions
  together) was built. Each link was tested in isolation.

## Suggested next steps

- Build a proper multi-variable regression for RQ3 (visits, pricing
  era, and acquisition status together as predictors of revenue) to
  get an actual variance decomposition rather than a qualitative one.
- Revisit RQ1 with NOAA's newer RONI index (adopted February 2026),
  which reclassifies some recent Neutral winters as La Niña and could
  produce a meaningfully different result (see the RONI discussion
  added to `rq1_findings.md`).
- Extend RQ2 and RQ3's sample sizes as more seasons of data become
  available in the coming years, both are currently underpowered by
  any reasonable statistical standard.
