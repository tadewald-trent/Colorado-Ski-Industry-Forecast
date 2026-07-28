# Data Dictionary

Every data source used in this project, with enough detail to regenerate the
raw downloads from scratch. Raw files are gitignored — this doc is the
source of truth for "how do I get the data back."

## RQ1 — Snowfall stations (NOAA GHCND, via NOAA CDO API)

Fixed list of 7 stations (not basin aggregates), chosen for long period of
record and a clear north/south regional split. Confirmed via NOAA CDO
station search (`https://www.ncdc.noaa.gov/cdo-web/search`).

| Region | Station | GHCND ID | Period of record | Coverage |
|---|---|---|---|---|
| North | Breckenridge | USC00050909 | 1893-01-01 → present | 72% ⚠️ check for systematic gaps before trusting early record |
| North | Steamboat Springs | USC00057936 | 1893-02-01 → present | 90% |
| North | Winter Park | USC00059175 | 1942-03-01 → present | 98% |
| North | Vail Mountain | USS0006K39S | 1978-09-30 → present | 100% |
| South | Wolf Creek Summit | USS0006M17S | 1986-08-20 → present | 100% |
| South | Telluride 4 WNW | USC00058204 | 1900-12-01 → present | 89% |
| South | Crested Butte | USC00051959 | 1909-06-01 → present | 98% |

**Shared analysis window: 1986–2026 (~40 winters)**, bounded by Wolf Creek
Summit's start date. Individual single-station queries (e.g. a long-run
trend at Steamboat) may use that station's full record; any query comparing
across stations or computing a north-vs-south aggregate must be clipped to
1986–present to keep the comparison honest.

Station IDs with a `USC` prefix are legacy Cooperative Observer Network
(COOP) stations — volunteer-reported, longer records, more variable
coverage. IDs with a `USS` prefix are SNOTEL sites also reporting through
GHCND — automated, shorter records, generally excellent coverage.

**How to pull this data:** NOAA CDO API v2, `datasetid=GHCND`,
`datatypeid=SNOW,PRCP`, one station + one year per request (API caps date
range at 1 year for GHCND). Requires a free token from
`https://www.ncdc.noaa.gov/cdo-web/token`. See `scripts/fetch_ghcnd.py`
(once written) for the pull script.

## RQ1 — ENSO / ONI index

- **Source:** NOAA Climate Prediction Center, DJF Oceanic Niño Index table
  (`https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php`)
- **Granularity:** Monthly running 3-month means; DJF (Dec-Jan-Feb) value
  used as the winter's representative ENSO state
- **Coverage:** 1950–present, complete
- **Format:** Copy-paste table on the CPC page; no API, small enough to
  transcribe/paste directly into a CSV

## RQ1 — Snowpack (SWE % of median)

- **Source:** NRCS SNOTEL network, via the interactive report tool at
  `https://wcc.sc.egov.usda.gov/reports/`
- **Granularity:** Daily, by station or statewide/basin aggregate
- **Coverage:** 1987–present (network buildout era)
- **Status:** Not yet pulled — only a few illustrative data points sourced
  so far (2012, 2023, 2026 April 1 statewide %). Full series still needed.

## RQ2 — Colorado statewide skier visits

- **Source:** Colorado Ski Country USA (CSCUSA) annual press releases,
  searched year by year (no single historical table found yet)
- **Granularity:** Seasonal (one number per winter)
- **Coverage:** Confirmed so far: 2018–19 through 2024–25 (6 seasons).
  CSCUSA has a longer public record — earlier years need to be tracked down
  individually via their press archive.
- **Status:** Partial — needs a systematic pull across more seasons.

## RQ3 — Vail Resorts revenue

- **Source:** SEC 10-K filings (`SEC EDGAR`) or aggregator sites
  (macrotrends.net, stockanalysis.com) for a quick pull; 10-Ks are the
  authoritative source if precision matters
- **Granularity:** Fiscal year (ends July 31)
- **Coverage:** FY2009–FY2025 confirmed usable
- **Status:** Numbers sourced for FY2009–2025; needs a
  `is_acquisition_year` flag column added per the confounders in
  `scoping.md` (e.g. Peak Resorts 2019).

## Open data-sourcing tasks (Phase 1 remaining)

- [ ] Pull full NRCS SNOTEL statewide SWE series (1987–present)
- [ ] Pull full CSCUSA skier-visit history (as far back as available)
- [ ] Get NOAA CDO API token and write `fetch_ghcnd.py` to pull all 7
      stations' daily SNOW/PRCP for 1986–2026
- [ ] Identify Vail Resorts acquisition years for the confounder flag
- [ ] Identify Epic Pass / Ikon Pass launch dates precisely (2008 / 2018 —
      confirm exact season each took effect)
## RQ1 — SNOTEL snowpack (SWE) for the 7 core stations' home counties

- **Source:** NRCS SNOTEL network, via the interactive Report Generator
  (`https://wcc.sc.egov.usda.gov/reportGenerator/`)
- **Method:** Manually searched by county (Advanced Search → County filter,
  Network = SNOTEL) for each of the 7 core stations' home counties, then
  combined into a single custom report. One station search returned
  results from a same-named county in a different state (e.g., a
  "Mineral County" hit in Montana, a "San Miguel County" hit in New
  Mexico) — filtered out by checking the State column before adding.
- **Counties pulled:** Summit (Breckenridge), Routt (Steamboat Springs),
  Grand (Winter Park), San Miguel (Telluride), Gunnison (Crested Butte),
  Eagle (Vail Mountain), Mineral (Wolf Creek Summit) — all Colorado only.
- **Stations included:** 41 total SNOTEL sites across those 7 counties
  (includes Vail Mountain and Wolf Creek Summit themselves, plus all
  other SNOTEL sites sharing their home county).
- **Granularity:** Daily SWE (snow water equivalent, inches), start-of-day
  values, full period of record per station (some stations start as
  early as 1978, others later depending on install date).
- **File:** `data/raw/snotel/snotel_swe_daily.csv`
- **Format note:** This file is in **wide** format — one row per date,
  one column per station. This is different from the GHCND snowfall data
  (`data/raw/ghcnd/*.csv`), which is in **long** format (one row per
  date+datatype). Will need reshaping to long format during Phase 2
  schema/load to keep a consistent table structure.
- **Known gaps:** Blank cells mean that station wasn't yet operational
  on that date (stations were installed at different times) — not
  missing/bad data, just "doesn't exist yet."
  ## RQ2 — Colorado statewide skier visits (CSCUSA)

**Important methodology note:** CSCUSA's headline visit numbers are NOT
measured consistently over time — see `scoping.md`'s confounders section
for the full explanation. In short: Vail Resorts (Vail, Beaver Creek,
Breckenridge, Keystone) is not a CSCUSA member and stopped disclosing its
own visit numbers after 2013-14. CSCUSA's "members-only" totals (2014-15
through 2017-18) are a smaller, differently-scoped metric than its
"full-state estimate" totals (2018-19 onward, and 2013-14). Any table
built from this data needs a `measurement_basis` column.

| Season | Visits (millions) | Basis | Source |
|---|---|---|---|
| 2013-14 | 12.6 | full_state_estimate | CSCUSA (last yr Vail disclosed) |
| 2013-14 | 7.1 | cscusa_members_only | CSCUSA (alt. metric, same season) |
| 2014-15 | 7.1 | cscusa_members_only | CSCUSA |
| 2015-16 | 7.4 | cscusa_members_only | CSCUSA (record for this metric) |
| 2016-17 | 7.3 | cscusa_members_only | CSCUSA |
| 2017-18 | 7.1 | cscusa_members_only | CSCUSA |
| 2018-19 | 13.8 | full_state_estimate | CSCUSA (methodology switch point) |
| 2019-20 | TBD | — | not yet sourced (COVID-shortened season) |
| 2020-21 | 12.0 | full_state_estimate | CSCUSA |
| 2021-22 | ~13.9-14.0 | full_state_estimate | CSCUSA |
| 2022-23 | 14.8 | full_state_estimate | CSCUSA (all-time record) |
| 2023-24 | 14.0 | full_state_estimate | CSCUSA |
| 2024-25 | 13.8 | full_state_estimate | CSCUSA |
| 2025-26 | 10.5 | full_state_estimate | CSCUSA (24% drop, worst since 1991-92) |

**Pre-2013-14 history:** available at the individual-resort level (not
statewide totals) from Storm Skiing's compiled dataset, covering
1976-77 through ~2009-10, sourced from newspapers, USFS documents, and
archival CSCUSA statistical sheets:
`https://docs.google.com/spreadsheets/d/1XqUXoq2ohRqBhPVyQd8gn9qmI-Yf98xI-WZAiEbyzFE`
Getting a Colorado statewide total for any given pre-2010 year from this
source requires summing that year's Colorado resorts — not yet done.
Also note: ski-area-level visit disclosure "dried up" industry-wide after
2010 and further after 2020, per that source, which is itself a relevant
data-availability fact for RQ2/RQ3.
**Pre-2010 analog-year totals**, computed by summing all Colorado resorts'
individual visits for specific winters of interest (rather than
transcribing the full 45+ year series):

| Season | Total visits | Completeness | ENSO phase |
|---|---|---|---|
| 1982-83 | 8,078,362 | complete, all resorts reporting | El Niño (ONI +2.2) |
| 1997-98 | 11,941,777 | complete, all resorts reporting | El Niño (ONI +2.2) |
| 1999-2000 | 10,861,892 | complete, all resorts reporting | La Niña (ONI -1.5) |
| 2009-10 | 11,857,879 | complete, all resorts reporting | El Niño (ONI +1.5) |
| 2015-16 | *(incomplete)* | missing Beaver Creek, Breckenridge, Keystone, Vail Mountain | El Niño (ONI +2.6) |

**Independent confirmation of the CSCUSA confounder:** the 2015-16 row's
missing resorts are exactly the four Vail Resorts properties — this
matches, from an entirely separate data source, the documented fact that
Vail stopped disclosing resort-level visit numbers after 2013-14. For
that season, use the CSCUSA members-only figure (7.4M) instead, with the
`measurement_basis` flag noting it excludes Vail Resorts properties.

**Preliminary RQ2 observation (2 data points only, not conclusive):**
1997-98 (strong El Niño) saw ~11.9M visits vs. 1999-2000 (moderate La
Niña) at ~10.9M — a difference in the expected direction, but confounded
by overall industry growth trend across those years and far too small a
sample to draw a real conclusion from yet.

**Source data:** Storm Skiing's per-resort spreadsheet
(`https://docs.google.com/spreadsheets/d/1XqUXoq2ohRqBhPVyQd8gn9qmI-Yf98xI-WZAiEbyzFE`),
compiled from newspapers, USFS documents, academic studies, and archival
CSCUSA statistical sheets. Covers ~24 Colorado ski areas back to the
1930s-70s depending on resort age; individual resort-level disclosure
becomes sparse industry-wide after 2010 and again after 2020.
## RQ3 — Vail Resorts acquisitions & pass launch dates

**Epic Pass:** Launched March 2008, initially $579 for Vail, Breckenridge,
Beaver Creek, Keystone, and Heavenly (replacing an $1,850 Vail+Beaver
Creek-only pass). Confirmed via Vail Resorts spokesperson statements and
contemporary coverage.

**Ikon Pass:** Launched by Alterra Mountain Company in 2018 at $899.

**Vail Resorts acquisitions relevant to our 7 core stations / CO market:**

| Year | Acquisition | Relevance |
|---|---|---|
| 1996 | Breckenridge, Keystone | Breckenridge = one of our 7 core stations |
| 2002 | Heavenly (Tahoe, not CO) | Added to Epic Pass network, not CO-specific |
| 2016 | Whistler Blackcomb ($1.1B) | Major network expansion, not CO-specific |
| 2018 | Crested Butte, Okemo, Mount Sunapee, Stevens Pass | Crested Butte = one of our 7 core stations |
| 2019 | Peak Resorts (17 US areas) | Not CO-specific |

**Confounder flag implication:** for the `vail_resorts_revenue` table,
mark fiscal years containing a major acquisition close as
`is_acquisition_year = TRUE` — at minimum FY2017 (Whistler, closed Oct
2016), FY2019 (Crested Butte/Okemo/Sunapee/Stevens, closed 2018-19), and
FY2020 (Peak Resorts, closed fall 2019) — since these years' revenue
jumps reflect new properties, not organic growth or weather effects.

**Sources:** Vail Resorts Newsroom press releases, Durango Herald and
Deseret News coverage of a 2026 Epic/Ikon antitrust lawsuit (which
included historical pricing detail), 5280 Magazine and SnowBrains
acquisition timelines.