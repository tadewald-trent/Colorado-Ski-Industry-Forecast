# Colorado Rockies Snowfall → Ski Industry Business Impact

**Status:** 🚧 In progress — Phase 1 (data acquisition)
**Stack:** PostgreSQL · SQL · Python (acquisition/cleaning) · Tableau Public

## Motivating question

Does the El Niño–Southern Oscillation (ENSO) climate pattern predict Colorado
snowfall, and if so, does that translate into measurable changes in
ski-industry participation (skier visits) and business performance
(revenue)? Where does that causal chain hold up, and where does it break
down?

This is framed as a **chain of four sub-questions**, each answered on its own
evidence before being combined — not a single end-to-end correlation. See
[`docs/scoping.md`](docs/scoping.md) for the full research questions,
hypotheses, and known confounders.

## Project structure

```
├── README.md              # you are here
├── docs/
│   ├── scoping.md          # research questions, hypotheses, confounders, non-goals
│   ├── data_dictionary.md  # every data source, station ID, coverage, date range
│   └── progress.md         # running log of what's been done, phase by phase
├── data/
│   ├── raw/                # (gitignored) untouched downloads — see data_dictionary.md to regenerate
│   └── processed/          # cleaned CSVs ready to load into Postgres
├── sql/
│   ├── schema.sql          # CREATE TABLE statements
│   └── analysis/           # RQ1, RQ2, RQ3 query sets
├── scripts/                # Python fetch/clean scripts
└── dashboard/              # Tableau workbook + link to published version
```

## Findings

*(To be filled in as RQ1–RQ4 are answered. This section will hold the honest,
final summary — including any "no relationship found" results — once the
analysis is complete.)*

## Status / how to follow along

Detailed phase-by-phase progress is tracked in
[`docs/progress.md`](docs/progress.md). Short version: research questions and
data sources are scoped, and the 7 snowfall stations for the north/south
climate comparison are confirmed. Currently pulling raw data.
