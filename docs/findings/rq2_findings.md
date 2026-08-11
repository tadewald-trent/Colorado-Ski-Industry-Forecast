# RQ2 Findings: Does snowfall predict Colorado skier visits?

**Research question (from scoping.md):** Does statewide/resort-level
snowpack correlate with same-season skier visits? Does that
relationship hold once the data is split by pass-pricing era (pre-Epic
Pass, Epic Pass era post-2008, multi-mountain-pass era post-2018)?

**Hypothesis (stated in advance):** The raw correlation is weaker than
expected because pass pricing structurally changed visit behavior;
visits became less weather-elastic once season passes were priced as a
sunk cost.

## Method

Queries in `sql/analysis/rq2_snow_vs_visits.sql`; regression testing in
`scripts/rq2_significance_test.py`.

A single "snow index" was built as the average total seasonal snowfall
across the 5 core GHCND stations with SNOW data, one value per winter.
This was compared against Colorado statewide skier visits.

**A key data-quality step:** the `cscusa_members_only` rows (2014-15
through 2017-18, see the measurement-basis confounder documented in
`scoping.md`) were excluded from all quantitative testing, since that
metric is scoped differently (excludes Vail Resorts properties) and is
not comparable to the full-state figures. This left 12 usable seasons:
4 pre-Epic/early-Epic seasons (1983, 1998, 2000, 2010) plus 8 seasons
from 2014 onward using full-state estimates. Note the 2019-20 season is
absent from the comparable dataset; a full-state visits figure for that
COVID-shortened season was not sourced during Phase 1 (see
`data_dictionary.md`'s open items).

Three regressions were run:
1. All 12 comparable seasons pooled (1983-2026).
2. Just the 7 seasons in the `epic_and_ikon` era (2019-2026), the most
   methodologically and structurally consistent subset.
3. The same 7 seasons with the single most extreme season (2025-26)
   removed, as a sensitivity/robustness check on result 2.

## Result

| Test | n | r-squared | p-value | Significant? |
|---|---|---|---|---|
| All 12 seasons, pooled (1983-2026) | 12 | 2.3% | 0.638 | No |
| Epic+Ikon era only (2019-2026) | 7 | 86.3% | 0.0025 | Yes |
| Epic+Ikon era, excluding 2025-26 | 6 | 60.8% | 0.068 | No |

**Pooling all 44 years shows no relationship at all**, consistent with
the hypothesis that a raw, era-blind correlation would be weak. This is
also confounded by decades of industry growth unrelated to weather (the
ski industry in 1983 was far smaller than today, regardless of that
winter's snowfall).

**Restricting to the modern Epic+Ikon era alone (2019-2026) shows a very
strong, statistically significant relationship.** Within these 7
seasons, the snow index and visits rise and fall together multiple
times, not just as a simple shared trend over time. This is a much more
interesting result than RQ1 produced.

**However, this result is not robust to the removal of a single
season.** Excluding 2025-26, which had by far the lowest snow index
(94.5") and the lowest visits (10.5M) in the entire modern era, drops
the result from p=0.0025 to p=0.068: no longer significant at the
conventional threshold, though the correlation remains directionally
consistent and moderately strong (r=0.78, r-squared=60.8%).

## Honest interpretation

- **This is not the same kind of clean null result as RQ1.** There is a
  real, directionally consistent, moderately strong relationship
  visible in the modern-era data. But with only 6-7 data points, it
  cannot be called statistically confirmed; one season is doing a
  large share of the work in the headline significant result.
- **The original hypothesis (weaker correlation post pass-pricing
  changes) is not clearly supported or refuted by this test.** The
  modern (post-Epic, post-Ikon) era actually shows the *strongest*
  apparent relationship in the entire dataset, the opposite of what a
  "passes decoupled visits from weather" story would predict. This
  could mean the hypothesis is wrong, or it could mean the modern-era
  sample is simply too small and too dominated by one dramatic drought
  season to draw a real conclusion either way.
- **The pass-era split itself could not be tested with real statistical
  power.** The `pre_epic` era has only 3 comparable seasons and the
  `epic_only` era only 2, far too few for a meaningful within-era test.
  Only the `epic_and_ikon` era had enough seasons (7) to attempt
  regression at all, and even that is a small sample by any standard.
- **This finding should be treated as suggestive, not confirmed.** The
  honest conclusion is: "there may be a real relationship between snow
  and visits in the current pass-pricing era, but the current dataset
  cannot statistically confirm it, and more seasons of data are needed
  before treating this as established."

## What would improve this analysis

- More seasons in the `epic_and_ikon` era. This era only began in 2018,
  so the sample will keep growing by one season per year; re-running
  this analysis in a few years, once the era has 10-12 seasons, would
  give a much more trustworthy answer than 7 (or 6) points can provide.
- Sourcing the missing 2019-20 season's full-state visits figure would
  add one more usable data point now.
- Sourcing more of the `pre_epic` and `epic_only` eras (see the
  Storm Skiing per-resort dataset noted in `data_dictionary.md`, which
  could fill in additional pre-2010 statewide totals) would allow an
  actual within-era test for those two eras, not just `epic_and_ikon`.
- A more sophisticated model could control for the industry-growth
  trend directly (e.g., detrending visits before testing against snow,
  rather than only comparing within a restricted modern-era subset).
