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

Queries in `sql/analysis/rq1_enso_snowpack.sql`. Two separate tests were
run:

1. **SNOTEL peak SWE** (queries 1-3): only 2 of the 7 core stations
   (Vail Mountain, Wolf Creek Summit) have SNOTEL data, so this is a
   1-station-per-region comparison, too weak a sample to draw a real
   conclusion from on its own, but included as a supplementary check.
2. **GHCND total seasonal snowfall** (queries 4-5): the real test,
   using 3 northern stations (Breckenridge, Steamboat Springs, Winter
   Park) and 2 southern stations (Crested Butte, Telluride), all
   stations with SNOW data, averaged by ENSO phase, 1986-2026.

## Result

**The hypothesis is not supported by this data.** Neither region shows
a strong, clean ENSO signal:

| Region | El Niño avg | La Niña avg | Neutral avg | El Niño minus La Niña |
|---|---|---|---|---|
| North (3 stations) | 188.0" | 185.9" | 169.9" | +2.1" |
| South (2 stations) | 165.8" | 158.7" | 154.0" | +7.1" |

- Both regions get modestly more snow in El Niño years than Neutral
  years, but the gap between El Niño and La Niña specifically (the core
  of the "teleconnection" theory) is small in both regions.
- The south does show a larger El Niño vs. La Niña gap (+7.1") than the
  north (+2.1"), which is directionally consistent with the hypothesis.
  But both gaps are small relative to year-to-year variability within
  each phase, and the south's overall snowfall totals are lower than
  the north's across all three ENSO phases, so this is a modest,
  low-confidence signal, not a clear confirmation.
- Station-level detail (query 5) shows real variation within each
  region: Winter Park (north) has the single highest El Niño-year
  average of any station (223.0"), while Telluride (south) has the
  lowest of any station in all three ENSO phases. Regional averages are
  therefore sensitive to which specific stations are included.

## Honest interpretation

- **Sample size is a real limitation.** 5 stations, about 40 winters,
  and only 11 to 16 winters per ENSO phase per station is a small
  sample for detecting what may be a genuinely subtle climate signal.
  This result should be read as "a weak, inconsistent signal in this
  dataset," not "no relationship exists in reality."
- **The classic ENSO-Colorado teleconnection is a statewide/regional
  climatological pattern** typically described using many decades of
  data and often expressed in probabilistic terms (shifted odds, not
  guaranteed outcomes). Five specific station records may be too noisy
  to recover that signal cleanly.
- **The SNOTEL 1-vs-1 comparison (Vail vs. Wolf Creek) points the same
  weak direction** as the multi-station test, which is mildly
  reassuring but does not fix the underlying small-sample problem since
  it is still just 2 stations.
- **This is still a useful, honest finding for the project.** RQ2 and
  RQ3 should not assume a strong, reliable ENSO to snowfall relationship
  exists for these specific 7 stations, based on this data. Any
  downstream ENSO-based prediction for skier visits or revenue should
  be treated as speculative rather than well-supported.

## What would improve this analysis

- More stations per region (the full 41-station SNOTEL supplemental
  dataset could be used for a much larger regional comparison, rather
  than just the 7 core stations)
- A longer time window per station where available (some stations have
  data back to 1893, not just the shared 1986-2026 window)
- A more rigorous statistical test (a t-test or regression with
  confidence intervals) rather than simple group averages, to
  distinguish a small real effect from noise
