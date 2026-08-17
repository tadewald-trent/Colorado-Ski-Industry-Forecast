# Colorado Rockies Snowfall → Ski Industry Business Impact

**Status:** ✅ Complete — all research questions answered, dashboard published
**Stack:** PostgreSQL · SQL · Python (acquisition/cleaning) · Tableau Public
**Live dashboard:** [Colorado Ski Industry Analysis on Tableau Public](https://public.tableau.com/views/ColoradoSkiIndustryAnalysis/Dashboard1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

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

This project tested a causal chain: **ENSO climate phase → Colorado
snowfall → skier visits → resort revenue.** Each link was tested
independently, with a stated hypothesis, before moving to the next.

**RQ1 — Does ENSO predict Colorado snowfall?** No. Across 8 separate
statistical tests (t-tests and regressions, two independent datasets,
station data extended back to 1950), no statistically significant
relationship was found between ENSO phase and snowfall or snowpack, in
either northern or southern Colorado. An early borderline result
(p=0.047) correctly did not survive extension to the full dataset
(p=0.083). See [`docs/findings/rq1_findings.md`](docs/findings/rq1_findings.md).

**RQ2 — Does snowfall predict skier visits?** Suggestive, but not
confirmed. A strong relationship in the modern pass-pricing era
(2019-2026, r²=86%) did not survive a sensitivity check removing the
historic 2025-26 drought season (r²=61%, no longer significant). See
[`docs/findings/rq2_findings.md`](docs/findings/rq2_findings.md).

**RQ3 — Do skier visits predict Vail Resorts revenue?** Yes — the most
robust finding in the project. A significant relationship (r²=75-78%)
survived every sensitivity check applied (excluding the one acquisition
year, restricting to the most recent 5-season cluster), despite having
the smallest sample size of any test in this analysis. See
[`docs/findings/rq3_findings.md`](docs/findings/rq3_findings.md).

**RQ4 — Does an ENSO forecast predict Colorado ski industry
performance?** No, based on this project's data. The causal chain
breaks at the very first link. Even though the visits → revenue link is
genuinely robust, a forecast that cannot reliably predict Colorado
snowfall cannot be used to predict Colorado ski industry performance
through this pathway. See
[`docs/findings/rq4_synthesis.md`](docs/findings/rq4_synthesis.md).

**Interactive dashboard:** all three quantitative findings are
visualized, with their actual statistical results and honest caveats,
in the Tableau Public dashboard linked above.