# RQ3 Findings: Does skier-visit volume predict Vail Resorts revenue?

**Research question (from scoping.md):** Does skier-visit volume
predict ski-company revenue (using Vail Resorts as the public-company
case study), or is revenue driven more by pricing changes and
acquisitions than by weather-driven visit volume?

**Hypothesis (stated in advance):** Revenue growth is dominated by
acquisition years and pass-price increases; the weather signal is
present but small relative to these other drivers.

## Method

Queries in `sql/analysis/rq3_visits_vs_revenue.sql`; regression testing
in `scripts/rq3_significance_test.py`.

**A key scope limitation, stated upfront:** Vail Resorts operates
resorts outside Colorado (Whistler Blackcomb, Park City, and
Midwest/Northeast properties, among others), while `skier_visits` is
Colorado statewide only. This test can only speak to whether Colorado
visitation correlates with total company revenue, not Colorado-specific
revenue. If anything, this scope mismatch should work against finding a
relationship, non-Colorado revenue is noise relative to a Colorado-only
predictor, which should dilute rather than manufacture a correlation.

Only 8 fiscal years have both a Vail revenue figure and a comparable
Colorado skier-visits figure (excluding `cscusa_members_only` rows, per
the same reasoning as RQ2): 2010, 2014, 2019, 2021-2025. This is a very
small sample.

Three regressions were run, each a progressively stricter sensitivity
check:
1. All 8 overlapping years.
2. The 7 years excluding FY2019, itself an acquisition year (Crested
   Butte, Okemo, Mount Sunapee, Stevens Pass), since that year's
   revenue jump partly reflects new properties, not visits.
3. Just the 5 most recent years (2021-2025), a tight, homogeneous
   cluster, to rule out the relationship being an artifact of two
   widely separated groups (older, lower-revenue years vs. newer,
   higher-revenue years) rather than a real graded pattern.

## Result

**Unlike RQ2, this relationship held up under every sensitivity
check.**

| Test | n | r-squared | p-value | Significant? |
|---|---|---|---|---|
| All 8 overlapping years | 8 | 75.3% | 0.0052 | Yes |
| Excluding FY2019 acquisition year | 7 | 76.6% | 0.0099 | Yes |
| Recent cluster only (2021-2025) | 5 | 78.3% | 0.0462 | Yes |

Removing the acquisition year barely changed the result (75.3% to
76.6% r-squared). Restricting to just the 5 most recent, most similar
years, the strictest possible check with this dataset, still produced
a statistically significant result, ruling out the concern that this
was simply two disconnected clusters (an old low-revenue group and a
new high-revenue group) rather than a real relationship.

## Honest interpretation

- **This is the most robust finding across all three research
  questions**, despite having by far the smallest sample size (5 to 8
  data points, versus hundreds for RQ1 and a dozen for RQ2). The result
  surviving two meaningfully different sensitivity checks is a real
  signal of robustness, not a guarantee, but a much better sign than
  RQ2's finding, which did not survive an equivalent check.
- **Correlation is not causation, and this test cannot distinguish
  between competing explanations.** A strong visits-revenue correlation
  is consistent with several different stories: (a) more visits
  directly generate more lift-ticket and ancillary revenue, (b) both
  visits and revenue respond to a shared underlying cause, such as a
  good snow year, strong economy, or favorable pass pricing, driving
  both up together, or (c) some mix of both. This analysis cannot
  separate these.
- **The original hypothesis is only partly supported.** It predicted
  that acquisitions and pricing would dominate over a visits/weather
  signal. Acquisitions clearly do matter (see `data_dictionary.md`'s
  acquisition timeline, and the schema's `is_acquisition_year` flag),
  but removing the one acquisition year in this sample did not weaken
  the visits-revenue relationship, it stayed essentially unchanged.
  This suggests visits and acquisitions may be more like two separate,
  additive drivers of revenue rather than one crowding out the other.
- **The Colorado-vs-global scope mismatch remains a real limitation**
  on how confidently this can be generalized. A cleaner test would use
  Colorado-specific revenue, which Vail Resorts does not publicly
  disclose at the state level.
- **Sample size is still the dominant caveat.** Even the most robust
  finding in this project rests on as few as 5 data points. This
  should be read as a promising, multiply-corroborated signal worth
  taking seriously, not a definitively proven relationship.

## What would improve this analysis

- More years of data as they become available (both Vail's fiscal
  filings and CSCUSA's visit reports are published annually, so this
  sample will grow over time).
- Sourcing additional historical CSCUSA visits data (see RQ2's open
  items) to fill in more of the pre-2010 and 2015-2018 gap years,
  which would substantially grow the usable overlap with Vail's
  revenue history.
- If Colorado-specific segment revenue for Vail Resorts becomes
  available (e.g., through more detailed 10-K segment reporting), a
  cleaner, same-scope test would be possible.
- Testing other ski companies with more geographically concentrated
  operations (a Colorado-only operator, if a suitable public or
  well-documented private company exists) would avoid the scope
  mismatch entirely.
