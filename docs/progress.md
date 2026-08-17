# Progress Log

Running log of what's been done, phase by phase. Not polished — this is the
working scratchpad; `README.md` gets the polished summary at the end.

**Live dashboard:** [Colorado Ski Industry Analysis on Tableau Public](https://public.tableau.com/views/ColoradoSkiIndustryAnalysis/Dashboard1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Phase 0 — Scoping ✅

- Defined the motivating question and broke it into RQ1–RQ4, each with a
  stated hypothesis (not just an open question).
- Identified 5 known confounders up front (pass pricing eras, M&A, COVID,
  north/south climate divide, small sample size) — built into scoping.md
  so they inform schema design rather than being discovered mid-analysis.
- Decided on stack: PostgreSQL (not SQLite) + Tableau Public, given Mac OS
  13 upgrade opened up BI tool options. Postgres chosen for native BI
  connector support and being a more standard portfolio signal.
- Decided confounders get explicit flag columns in the schema, not buried
  in query WHERE-clause logic.

## Phase 1 — Data acquisition ✅ in progress

- Chose fixed station/resort list (not basin aggregates) for RQ1's
  north/south comparison: 4 north (Breckenridge, Steamboat Springs, Winter
  Park, Vail Mountain), 3 south (Wolf Creek Summit, Telluride, Crested
  Butte). Breckenridge added as a 4th north station for local-knowledge
  reasons — noted explicitly rather than treated as random.
- Confirmed all 7 GHCND station IDs via NOAA CDO station search, including
  period of record and data coverage % for each. Full table in
  `data_dictionary.md`.
- Determined the shared cross-station analysis window: **1986–2026**,
  bounded by Wolf Creek Summit's 1986 start date.
- Flagged Breckenridge's 72% coverage as needing a gap check before trusting
  early-record data from that station.
- Remaining: NOAA CDO API token + fetch script, NRCS SNOTEL full series,
  CSCUSA full skier-visit history, Vail Resorts acquisition-year list. See
  `data_dictionary.md`'s open tasks checklist.
- Set up local Git repo and connected it to GitHub
  (`tadewald-trent/Colorado-Ski-Industry-Forecast`), including generating a
  Personal Access Token for authentication (GitHub no longer accepts account
  passwords for pushes).
- Completed the full GHCND daily SNOW/PRCP pull for all 7 stations
  (1986-2026), via `scripts/fetch_ghcnd.py`. Fixed an early version that
  could hang indefinitely on a stuck request; v2 added bounded retries
  and resume-by-skipping-existing-files. Raw CSVs saved locally under
  `data/raw/ghcnd/` (gitignored).
- Pulled NRCS SNOTEL daily SWE (snow water equivalent) data for 41
  stations across the 7 core stations' home counties (Summit, Routt,
  Grand, San Miguel, Gunnison, Eagle, Mineral), via the NRCS Report
  Generator UI. Worked through several tool quirks along the way (16M
  value size cap, unclear "unable to run report" errors traced to an
  unchecked column checkbox, and cross-state county name collisions —
  e.g. a Montana "Mineral County" and New Mexico "San Miguel County"
  both appearing in results and needing to be filtered out by state).
  Saved to `data/raw/snotel/snotel_swe_daily.csv` (wide format — will
  need reshaping to long format during Phase 2 schema/load).
- Documented Vail Resorts acquisition timeline (1996 Breckenridge/Keystone,
  2016 Whistler Blackcomb, 2018 Crested Butte/Okemo/Sunapee/Stevens Pass,
  2019 Peak Resorts) and confirmed Epic Pass (launched March 2008) / Ikon
  Pass (launched 2018) dates, with acquisition-year flags identified for
  the Phase 2 schema's `is_acquisition_year` confounder column.

**Phase 1 complete.** All planned data sources are sourced and documented:
GHCND snowfall (7 stations), SNOTEL SWE (41 stations), CSCUSA skier
visits (2013-2026 + pre-2010 analog years), Vail Resorts revenue +
acquisition timeline, and Epic/Ikon pass launch dates. Ready to move to
Phase 2 (Postgres schema design and data load).

## Phase 2 — Schema + load ✅

- Installed PostgreSQL via Postgres.app; fixed PATH so `psql` works from
  Terminal. Created the `colorado_ski` database.
- Designed and built a 7-table schema (`stations`, `enso_oni`,
  `snowfall_daily`, `snowpack_daily`, `skier_visits`, `vail_revenue`,
  `pass_launches`), with confounder flags as real columns/constraints
  rather than query-level logic: `measurement_basis` (CHECK constraint)
  on skier_visits, `is_acquisition_year` on vail_revenue, `is_complete`
  for known-incomplete rows.
- Wrote and ran 6 Python load scripts (`psycopg2`), one per table group.
  Final row counts: stations 46, enso_oni 77, pass_launches 2,
  skier_visits 17, vail_revenue 17, snowfall_daily 168,195,
  snowpack_daily 532,457.
- Verified the trickiest transformation - reshaping the wide-format
  SNOTEL CSV (one column per station) into long format - worked
  correctly, including mapping Vail Mountain and Wolf Creek Summit's
  SNOTEL data back onto their existing GHCND station_id rather than
  creating duplicate station entries for the same physical location.
- Confirmed and documented a real data characteristic during load:
  the 2 SNOTEL-sourced GHCND stations have PRCP data only, no SNOW
  datatype - not a bug, a property of how those stations report to
  GHCND.

**Phase 2 complete.** Database fully loaded (~701,000 rows across 7
tables). Ready for Phase 3-5: writing the actual RQ1/RQ2/RQ3 analysis
queries.

## RQ1-RQ4 — Analysis complete ✅

- **RQ1 (ENSO → snowfall):** Tested 8 ways (t-tests + regressions,
  GHCND + SNOTEL data, extended to 1950). Clean, well-powered null
  result — no statistically significant relationship found in either
  region. A borderline early result (p=0.047) correctly did not survive
  extension to the full dataset (p=0.083).
- **RQ2 (snowfall → visits):** Suggestive but statistically fragile.
  Strong result in the modern pass-pricing era (r²=86%, p=0.0025)
  did not survive a sensitivity check removing one extreme season
  (r²=61%, p=0.068). Reported honestly as unconfirmed.
- **RQ3 (visits → revenue):** The most robust finding of the project.
  Survived multiple sensitivity checks (excluding the acquisition
  year, restricting to a tight recent 5-year cluster) with consistent
  r²=75-78% and p<0.05 throughout, despite the smallest sample size.
- **RQ4 (synthesis):** Direct, honest answer to the original
  motivating question: an ENSO forecast does not provide a
  statistically supported basis for predicting Colorado ski industry
  performance, because the chain breaks at the very first link
  (ENSO → snowfall), regardless of how robust the downstream
  visits → revenue link is.

**Remaining work:** Phase 6.5 (Tableau dashboard), Phase 7 (update
top-level README.md with real findings, final polish).

## Phase 6.5 — Tableau dashboard ✅

- Connected Tableau Public to the project data via CSV export (Tableau
  Public cannot connect directly to a local Postgres database — that's
  a paid Tableau Desktop/Server feature only). Built
  `scripts/export_dashboard_data.py` to export RQ1-RQ3 query results
  as clean CSVs.
- Built 3 chart sheets (one per RQ) plus a synthesis dashboard, each
  chart titled with its actual statistical result rather than a
  generic label (e.g. "RQ1: ... (Not Statistically Significant)").
- Removed misleading trend lines drawn through too few points (RQ3's
  1-point acquisition-year split, RQ2's 2-3 point pre-Epic/Epic-only
  eras), keeping only trend lines backed by real sample sizes.
- Published to Tableau Public: [https://public.tableau.com/app/profile/trent.tadewald/viz/ColoradoSkiIndustryAnalysis/Dashboard1]

**Phase 6.5 complete.**

## Phase 7 — GitHub polish ✅ complete
