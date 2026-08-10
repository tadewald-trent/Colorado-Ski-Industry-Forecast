# RQ1 Findings: Does ENSO predict Colorado snowfall, north vs. south?

**Research question (from scoping.md):** Does ENSO phase (DJF Oceanic
Niño Index) predict Colorado snowpack/snowfall? Does the relationship
differ between northern Colorado mountains (Steamboat, Winter Park,
Vail/Summit County) and southern Colorado mountains (San Juans, Wolf
Creek, Telluride, Crested Butte)?

**Hypothesis (stated in advance):** Southern Colorado shows a stronger
positive ENSO relationship than northern Colorado, consistent with
classic El Niño storm-track teleconnections. Northern Colorado's
relationship is expected to be weak or inconsistent.

## Method

Queries in `sql/analysis/rq1_enso_snowpack.sql`; all statistical testing
in `scripts/rq1_significance_test.py`. Two data sources, tested two
ways each (8 tests total):

1. **SNOTEL peak SWE**, all 46 stations (28 north, 13 south), region
   assigned by county (`sql/assign_regions.sql`), full available
   history.
2. **GHCND total seasonal snowfall**, 5 stations with SNOW data
   (Breckenridge, Steamboat Springs, Winter Park in the north; Crested
   Butte, Telluride in the south), extended back to 1950 (the start of
   the official NOAA ONI record) after the original analysis was
   limited to 1986-2026.

Each data source was tested two ways:

- **Independent samples t-test (Welch's)**, comparing El Niño vs. La
  Niña winters as categories.
- **Linear regression**, using the continuous DJF ONI value as a
  predictor rather than a three-category phase label, which uses more
  information and can detect a relationship even if simple category
  averages look flat.

## Result

**None of the 8 tests found a statistically significant relationship
between ENSO and Colorado snowfall or snowpack, in either region.**

**T-tests (El Niño vs. La Niña):**

| Region | Metric | El Niño mean | La Niña mean | p-value | Significant? |
|---|---|---|---|---|---|
| North | Peak SWE | 19.64" | 20.97" | 0.083 | No |
| South | Peak SWE | 21.91" | 22.84" | 0.439 | No |
| North | Total snowfall | 183.2" | 193.5" | 0.200 | No |
| South | Total snowfall | 180.7" | 183.8" | 0.827 | No |

**Regressions (continuous ONI value):**

| Region | Metric | r-squared | p-value | Significant? |
|---|---|---|---|---|
| North | Peak SWE | 0.10% | 0.310 | No |
| South | Peak SWE | 0.02% | 0.777 | No |
| North | Total snowfall | 0.53% | 0.271 | No |
| South | Total snowfall | 0.13% | 0.655 | No |

ONI explains between 0.02% and 0.53% of the variance in snowfall or
snowpack across all four regressions, in both regions. This is not a
weak or hard-to-detect effect; it is effectively no explanatory power
at all.

**A secondary, earlier finding did not hold up under more complete
testing.** An initial version of the north SWE t-test, run before the
data was extended to its full available history, showed p=0.047 (a
borderline significant result, in the opposite direction from the
hypothesis). Once the artificial 1986 start-date restriction was
removed and the test re-run on the full dataset, that result dropped to
p=0.083, no longer significant. This is reported here as a demonstration
of why testing on the fullest available data matters, not as a finding
in its own right.

## Honest interpretation

- **The stated hypothesis is not supported.** There is no evidence in
  this dataset, across 8 separate tests using two different data
  sources and two different statistical methods, that ENSO predicts
  Colorado snowfall or snowpack at these stations, in either region.
- **This is a clean, well-supported null result**, not an ambiguous or
  underpowered one. Sample sizes for the regressions ranged from 151 to
  997 station-winters, which is a reasonably large sample for detecting
  even a modest real effect had one existed.
- **The GHCND and SNOTEL datasets, which disagreed in direction under
  the original limited 1986-2026 window, agree once the GHCND data was
  extended to its full available history back to 1950.** Both now show
  La Niña winters with slightly higher average snowfall than El Niño
  winters in both regions, though the difference is not statistically
  significant in either case.
- **This does not mean ENSO has zero effect on Colorado weather in
  general.** ENSO's broader climatological effects on the western U.S.
  are well documented at larger geographic scales. It means that, for
  these specific 7 core stations and this specific dataset, no
  detectable station-level relationship was found.

## Conclusion

Based on the most complete and rigorously tested evidence available in
this dataset, **Colorado's ENSO-snowfall relationship at these stations
shows no statistically significant effect, in either region, using
either a categorical or continuous measure of ENSO strength.** RQ2 and
RQ3 should not assume any ENSO-to-snowfall pathway exists for these
specific stations. Any downstream ENSO-based prediction for skier
visits or revenue should be treated as unsupported by this analysis,
not merely uncertain.

## What would improve this analysis further

- Extending the GHCND data back before 1950 (to 1893-1909, depending on
  station) was considered but not completed, due to difficulty sourcing
  precise, verifiable pre-1950 ONI values without relying on a
  reconstructed dataset with acknowledged additional uncertainty.
- A multi-year lag analysis (e.g., does a strong ENSO winter predict
  the *following* winter's snowpack, not just the concurrent one) was
  not tested and could be a legitimate follow-up.
- This analysis tested station-level snowfall only. A basin- or
  statewide-aggregate SNOTEL analysis (using NRCS's official SWE
  percent-of-median product, rather than raw station SWE) might behave
  differently than individual station records.
