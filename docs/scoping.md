# Scoping — Research Questions, Hypotheses, Confounders

## Research questions

**RQ1 — Climate driver.**
Does ENSO phase (DJF Oceanic Niño Index) predict Colorado snowpack/snowfall?
Does the relationship differ between northern Colorado mountains (Steamboat,
Winter Park, Vail/Summit County) and southern Colorado mountains (San Juans,
Wolf Creek, Telluride, Crested Butte)?

*Hypothesis:* Southern Colorado shows a stronger positive ENSO relationship
than northern Colorado, consistent with classic El Niño storm-track
teleconnections. Northern Colorado's relationship is expected to be weak or
inconsistent.

*Station/resort selection — see [`data_dictionary.md`](data_dictionary.md)
for confirmed GHCND IDs, periods of record, and coverage.*

**RQ2 — Snowfall → participation.**
Does statewide/resort-level snowpack correlate with same-season skier visits?
Does that relationship hold once the data is split by pass-pricing era
(pre-Epic Pass / Epic Pass era post-2008 / multi-mountain-pass era post-2018)?

*Hypothesis:* The raw correlation is weaker than expected because pass
pricing structurally changed visit behavior — visits became less
weather-elastic once season passes were priced as a sunk cost.

**RQ3 — Participation → revenue.**
Does skier-visit volume predict ski-company revenue (using Vail Resorts as
the public-company case study), or is revenue driven more by pricing changes
and acquisitions than by weather-driven visit volume?

*Hypothesis:* Revenue growth is dominated by acquisition years and
pass-price increases; the weather signal is present but small relative to
these other drivers.

**RQ4 — Synthesis.**
Combining RQ1–RQ3: how much of the variance in ski-industry revenue can
plausibly be attributed to weather vs. non-weather factors? What is the
honest answer to "does next winter's ENSO forecast tell us anything useful
about ski industry performance"?

## Known confounders (built into the schema, not discovered by accident)

- **Pass pricing eras** — Epic Pass launched 2008; Ikon Pass launched 2018.
  Both structurally reduced the marginal cost of an additional ski day,
  likely decoupling visits from weather.
- **M&A activity** — Vail Resorts' revenue growth includes step-changes from
  acquisitions (e.g., Peak Resorts 2019, Andermatt/other expansions), which
  will look like "growth" in a naive YoY query but have nothing to do with
  snow.
- **COVID-19 (2020–21 season)** — an exogenous shock to visits unrelated to
  weather; should be flagged, not silently included in trend analysis.
- **North/south climate divide within Colorado** — statewide aggregates can
  mask offsetting regional effects; RQ1 is split regionally for this reason.
- **Small sample size** — roughly 35–75 winters of usable ENSO/snowpack data
  depending on source, and far fewer years of clean skier-visit/revenue data.
  Findings should be reported as descriptive/directional, not statistically
  definitive, unless a proper regression with confidence intervals is run
  and the sample supports it.

## Explicit non-goals (scope boundaries)

- Not a storm-level weather forecast — seasonal/statistical only.
- Not attempting to model every Colorado resort individually — Vail Resorts
  is the revenue case study; snowpack/visits are analyzed statewide and
  north/south regionally.
- Not building a predictive ML model in this phase — SQL-based descriptive
  and correlational analysis, with the door left open for a regression
  extension later if the data supports it.

## Success criteria for this project

- [ ] RQ1–RQ3 each have a SQL query set and a written, honest answer
      (including "no relationship found" if that's what the data shows)
- [ ] Schema includes explicit confounder flag columns, not confounders
      buried in query logic
- [ ] Tableau Public dashboard reproduces the key findings interactively
- [ ] README documents data sources, limitations, and what a viewer should
      *not* conclude from this analysis
