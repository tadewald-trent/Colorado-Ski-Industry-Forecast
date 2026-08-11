-- ============================================================
-- RQ2: Does snowfall/snowpack predict Colorado skier visits?
-- Does the relationship hold once pass-pricing eras are accounted for?
-- ============================================================

-- Query 1: Side-by-side view - each season's average snow index
-- (mean total seasonal GHCND snowfall across the 5 core stations with
-- SNOW data) next to that season's skier visits, with pass era
-- labeled. This is exploratory - just to see the data before any
-- statistical testing.
WITH winter_snowfall AS (
    SELECT
        CASE
            WHEN EXTRACT(MONTH FROM sf.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sf.obs_date)
            ELSE EXTRACT(YEAR FROM sf.obs_date) + 1
        END AS winter_year,
        sf.station_id,
        SUM(sf.value_inches) AS station_total_snowfall
    FROM snowfall_daily sf
    JOIN stations s ON s.station_id = sf.station_id
    WHERE sf.datatype = 'SNOW'
      AND s.region IS NOT NULL  -- the 5 core stations with SNOW data
    GROUP BY winter_year, sf.station_id
),
snow_index AS (
    SELECT
        winter_year,
        ROUND(AVG(station_total_snowfall), 1) AS avg_snowfall_index
    FROM winter_snowfall
    GROUP BY winter_year
)
SELECT
    v.season_label,
    v.winter_year,
    v.visits,
    v.measurement_basis,
    si.avg_snowfall_index,
    CASE
        WHEN v.winter_year < 2009 THEN 'pre_epic'
        WHEN v.winter_year < 2019 THEN 'epic_only'
        ELSE 'epic_and_ikon'
    END AS pass_era
FROM skier_visits v
LEFT JOIN snow_index si ON si.winter_year = v.winter_year
ORDER BY v.winter_year, v.measurement_basis;


-- Query 2: The "comparable" dataset for actual statistical testing -
-- excludes cscusa_members_only rows, since that metric excludes Vail
-- Resorts properties and is not comparable to the full-state figures.
-- Only 12 seasons remain after this filter - a real sample-size
-- limitation, much smaller than RQ1's station-winter counts.
WITH winter_snowfall AS (
    SELECT
        CASE
            WHEN EXTRACT(MONTH FROM sf.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sf.obs_date)
            ELSE EXTRACT(YEAR FROM sf.obs_date) + 1
        END AS winter_year,
        sf.station_id,
        SUM(sf.value_inches) AS station_total_snowfall
    FROM snowfall_daily sf
    JOIN stations s ON s.station_id = sf.station_id
    WHERE sf.datatype = 'SNOW'
      AND s.region IS NOT NULL
    GROUP BY winter_year, sf.station_id
),
snow_index AS (
    SELECT
        winter_year,
        ROUND(AVG(station_total_snowfall), 1) AS avg_snowfall_index
    FROM winter_snowfall
    GROUP BY winter_year
)
SELECT
    v.season_label,
    v.winter_year,
    v.visits,
    si.avg_snowfall_index,
    CASE
        WHEN v.winter_year < 2009 THEN 'pre_epic'
        WHEN v.winter_year < 2019 THEN 'epic_only'
        ELSE 'epic_and_ikon'
    END AS pass_era
FROM skier_visits v
JOIN snow_index si ON si.winter_year = v.winter_year
WHERE v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
ORDER BY v.winter_year;
