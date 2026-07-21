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
