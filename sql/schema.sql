-- ============================================================
-- Colorado Ski Snowfall & Ski-Industry Business Analysis
-- Schema for PostgreSQL (database: colorado_ski)
-- ============================================================

-- ------------------------------------------------------------
-- 1. Stations lookup table
--    Covers all 48 stations: the 7 core GHCND stations used for
--    the north/south snowfall comparison (RQ1), plus the 41
--    supplementary SNOTEL sites pulled from their home counties.
-- ------------------------------------------------------------
CREATE TABLE stations (
    station_id      TEXT PRIMARY KEY,      -- e.g. 'GHCND:USC00050909' or SNOTEL site name
    station_name    TEXT NOT NULL,
    station_type    TEXT NOT NULL CHECK (station_type IN ('ghcnd_core', 'snotel_core', 'snotel_supplemental')),
    region          TEXT CHECK (region IN ('north', 'south')),  -- only set for the 7 core stations
    county          TEXT,
    state           TEXT NOT NULL DEFAULT 'CO',
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    elevation_ft    NUMERIC(8,1),
    period_of_record_start DATE,
    data_coverage_pct NUMERIC(5,2)          -- from NOAA's station metadata, where known
);

COMMENT ON TABLE stations IS
    'Lookup table for all snowfall/snowpack stations. station_type distinguishes
     the 7 core GHCND stations (north/south comparison, RQ1) from the 2 core
     stations that are also SNOTEL sites, and the 41 supplemental SNOTEL sites
     pulled from the core stations'' home counties.';


-- ------------------------------------------------------------
-- 2. ENSO / ONI index (RQ1 climate driver)
-- ------------------------------------------------------------
CREATE TABLE enso_oni (
    winter_year     INTEGER PRIMARY KEY,   -- year containing Jan/Feb, e.g. 2016 = winter 2015-16
    djf_oni         NUMERIC(4,2) NOT NULL, -- Dec-Jan-Feb Oceanic Nino Index, NOAA CPC
    enso_phase      TEXT NOT NULL CHECK (enso_phase IN ('El Nino', 'La Nina', 'Neutral'))
);


-- ------------------------------------------------------------
-- 3. Daily snowfall / precipitation (GHCND, 7 core stations)
--    Long format, mirrors the raw CSVs directly.
-- ------------------------------------------------------------
CREATE TABLE snowfall_daily (
    id              SERIAL PRIMARY KEY,
    station_id      TEXT NOT NULL REFERENCES stations(station_id),
    obs_date        DATE NOT NULL,
    datatype        TEXT NOT NULL CHECK (datatype IN ('SNOW', 'PRCP')),
    value_inches    NUMERIC(6,2),
    attributes      TEXT,                  -- raw NOAA quality-flag string, kept as-is
    UNIQUE (station_id, obs_date, datatype)
);

CREATE INDEX idx_snowfall_daily_date ON snowfall_daily(obs_date);
CREATE INDEX idx_snowfall_daily_station ON snowfall_daily(station_id);


-- ------------------------------------------------------------
-- 4. Daily snowpack (SNOTEL SWE, 41 stations across core counties)
--    Source CSV is wide (one column per station) - this table is
--    long format instead, reshaped during load for consistency
--    with snowfall_daily.
-- ------------------------------------------------------------
CREATE TABLE snowpack_daily (
    id              SERIAL PRIMARY KEY,
    station_id      TEXT NOT NULL REFERENCES stations(station_id),
    obs_date        DATE NOT NULL,
    swe_inches      NUMERIC(6,2),          -- snow water equivalent, start-of-day value
    UNIQUE (station_id, obs_date)
);

CREATE INDEX idx_snowpack_daily_date ON snowpack_daily(obs_date);
CREATE INDEX idx_snowpack_daily_station ON snowpack_daily(station_id);


-- ------------------------------------------------------------
-- 5. Colorado statewide skier visits (RQ2)
--    measurement_basis is a REQUIRED confounder flag - see
--    scoping.md for the full methodology-discontinuity writeup.
-- ------------------------------------------------------------
CREATE TABLE skier_visits (
    id                  SERIAL PRIMARY KEY,
    season_label        TEXT NOT NULL,        -- e.g. '2018-19'
    winter_year          INTEGER NOT NULL,     -- season-ending year, e.g. 2019
    visits               NUMERIC(10,1) NOT NULL, -- in actual visits, not millions (avoid ambiguity)
    measurement_basis    TEXT NOT NULL CHECK (
        measurement_basis IN ('full_state_estimate', 'cscusa_members_only', 'resort_level_sum')
    ),
    is_complete          BOOLEAN NOT NULL DEFAULT TRUE,  -- FALSE for e.g. 2015-16 resort-level sum (missing Vail properties)
    source               TEXT,
    UNIQUE (winter_year, measurement_basis)
);

COMMENT ON COLUMN skier_visits.measurement_basis IS
    'full_state_estimate: CSCUSA statewide total including estimated Vail Resorts contribution.
     cscusa_members_only: CSCUSA member-resorts-only total, excludes Vail Resorts properties.
     resort_level_sum: computed by summing individual CO resorts from the Storm Skiing dataset;
     may be incomplete for years where specific resorts (e.g. Vail Resorts properties post-2013-14)
     did not disclose - see is_complete flag.';


-- ------------------------------------------------------------
-- 6. Vail Resorts fiscal-year revenue (RQ3)
--    is_acquisition_year flags years where a major acquisition
--    closed, since revenue growth in those years partly reflects
--    new properties rather than organic/weather-driven growth.
-- ------------------------------------------------------------
CREATE TABLE vail_revenue (
    fiscal_year          INTEGER PRIMARY KEY,   -- FY ends July 31 of this year
    revenue_millions     NUMERIC(10,1) NOT NULL,
    is_acquisition_year  BOOLEAN NOT NULL DEFAULT FALSE,
    acquisition_note      TEXT,                  -- what was acquired that year, if applicable
    source               TEXT
);


-- ------------------------------------------------------------
-- 7. Pass launch dates (small reference table, used to derive
--    a pass-era flag in queries rather than storing it redundantly
--    on every row of skier_visits/vail_revenue)
-- ------------------------------------------------------------
CREATE TABLE pass_launches (
    pass_name       TEXT PRIMARY KEY,
    launch_year     INTEGER NOT NULL,      -- season-ending year of first season the pass was sold
    launch_price    NUMERIC(8,2),
    notes           TEXT
);
