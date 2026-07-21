# Progress Log

Running log of what's been done, phase by phase. Not polished — this is the
working scratchpad; `README.md` gets the polished summary at the end.

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

## Phase 1 — Data acquisition 🚧 in progress

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

## Phase 2 — Schema + load ⬜ not started

## Phase 3–5 — RQ1/RQ2/RQ3 SQL analysis ⬜ not started

## Phase 6 — Synthesis (RQ4) ⬜ not started

## Phase 6.5 — Tableau dashboard ⬜ not started

## Phase 7 — GitHub polish ⬜ not started
