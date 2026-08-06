-- ============================================================
-- RQ1: Does ENSO phase predict Colorado snowpack, and does the
-- relationship differ north vs. south?
-- ============================================================

-- Query 1: Average peak-season SWE by ENSO phase, split by region
-- (north vs south), using only the 7 core stations (which have a
-- region assigned) and only the shared 1986-2026 analysis window.
--
-- "Peak-season SWE" = the maximum SWE reading per station per winter
-- (a standard snowpack metric - roughly "how much snow was on the
-- ground at the deepest point that winter").
WITH winter_peak_swe AS (
    SELECT
        sp.station_id,
        s.region,
        -- A "winter year" here = the calendar year of the reading's
        -- Jan/Feb, matching how enso_oni.winter_year is defined.
        -- Since SWE peaks are almost always Dec-Apr, we approximate
        -- winter_year as the year of the reading if month <= 6,
        -- otherwise the following year.
        CASE
            WHEN EXTRACT(MONTH FROM sp.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sp.obs_date)
            ELSE EXTRACT(YEAR FROM sp.obs_date) + 1
        END AS winter_year,
        MAX(sp.swe_inches) AS peak_swe
    FROM snowpack_daily sp
    JOIN stations s ON s.station_id = sp.station_id
    WHERE s.region IS NOT NULL  -- only the 7 core stations have a region
    GROUP BY sp.station_id, s.region, winter_year
)
SELECT
    wps.region,
    o.enso_phase,
    COUNT(DISTINCT wps.winter_year) AS winters_included,
    ROUND(AVG(wps.peak_swe), 2) AS avg_peak_swe_inches
FROM winter_peak_swe wps
JOIN enso_oni o ON o.winter_year = wps.winter_year
WHERE wps.winter_year BETWEEN 1986 AND 2026
GROUP BY wps.region, o.enso_phase
ORDER BY wps.region, o.enso_phase;


-- Query 2: Same comparison, but as a single clean pivot - one row
-- per region, columns for each ENSO phase's average, so the
-- north-vs-south difference is easy to see at a glance.
WITH winter_peak_swe AS (
    SELECT
        sp.station_id,
        s.region,
        CASE
            WHEN EXTRACT(MONTH FROM sp.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sp.obs_date)
            ELSE EXTRACT(YEAR FROM sp.obs_date) + 1
        END AS winter_year,
        MAX(sp.swe_inches) AS peak_swe
    FROM snowpack_daily sp
    JOIN stations s ON s.station_id = sp.station_id
    WHERE s.region IS NOT NULL
    GROUP BY sp.station_id, s.region, winter_year
)
SELECT
    wps.region,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'El Nino'), 2) AS avg_swe_el_nino,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'La Nina'), 2) AS avg_swe_la_nina,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'Neutral'), 2) AS avg_swe_neutral
FROM winter_peak_swe wps
JOIN enso_oni o ON o.winter_year = wps.winter_year
WHERE wps.winter_year BETWEEN 1986 AND 2026
GROUP BY wps.region
ORDER BY wps.region;


-- Query 3: Station-by-station detail (not just region averages) -
-- useful to check whether the regional pattern is consistent across
-- all stations in that region, or driven by just one or two.
WITH winter_peak_swe AS (
    SELECT
        sp.station_id,
        s.station_name,
        s.region,
        CASE
            WHEN EXTRACT(MONTH FROM sp.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sp.obs_date)
            ELSE EXTRACT(YEAR FROM sp.obs_date) + 1
        END AS winter_year,
        MAX(sp.swe_inches) AS peak_swe
    FROM snowpack_daily sp
    JOIN stations s ON s.station_id = sp.station_id
    WHERE s.region IS NOT NULL
    GROUP BY sp.station_id, s.station_name, s.region, winter_year
)
SELECT
    wps.station_name,
    wps.region,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'El Nino'), 2) AS avg_swe_el_nino,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'La Nina'), 2) AS avg_swe_la_nina,
    ROUND(AVG(wps.peak_swe) FILTER (WHERE o.enso_phase = 'Neutral'), 2) AS avg_swe_neutral
FROM winter_peak_swe wps
JOIN enso_oni o ON o.winter_year = wps.winter_year
WHERE wps.winter_year BETWEEN 1986 AND 2026
GROUP BY wps.station_name, wps.region
ORDER BY wps.region, wps.station_name;

-- ============================================================
-- IMPORTANT LIMITATION found when running queries 1-3 above:
-- Only 2 of the 7 core stations (Vail Mountain, Wolf Creek Summit)
-- are SNOTEL sites with snowpack_daily data. The north-vs-south
-- comparison above is therefore just 1 station per region, not a
-- true regional average - too weak a sample to trust on its own.
--
-- Queries 4-5 below use snowfall_daily (SNOW datatype) instead,
-- which has multiple stations per region: Breckenridge, Steamboat
-- Springs, Winter Park (north, 3 stations) vs Telluride, Crested
-- Butte (south, 2 stations) - excluding Vail Mountain and Wolf
-- Creek Summit, which have no SNOW data (only PRCP - see
-- data_dictionary.md). This is a more defensible regional test.
-- ============================================================

-- Query 4: Total seasonal snowfall by ENSO phase, north vs south,
-- using the multi-station GHCND SNOW data.
WITH winter_snowfall AS (
    SELECT
        sf.station_id,
        s.station_name,
        s.region,
        CASE
            WHEN EXTRACT(MONTH FROM sf.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sf.obs_date)
            ELSE EXTRACT(YEAR FROM sf.obs_date) + 1
        END AS winter_year,
        SUM(sf.value_inches) AS total_snowfall
    FROM snowfall_daily sf
    JOIN stations s ON s.station_id = sf.station_id
    WHERE sf.datatype = 'SNOW'
      AND s.region IS NOT NULL
    GROUP BY sf.station_id, s.station_name, s.region, winter_year
)
SELECT
    ws.region,
    COUNT(DISTINCT ws.station_id) AS stations_in_region,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'El Nino'), 1) AS avg_snowfall_el_nino,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'La Nina'), 1) AS avg_snowfall_la_nina,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'Neutral'), 1) AS avg_snowfall_neutral
FROM winter_snowfall ws
JOIN enso_oni o ON o.winter_year = ws.winter_year
WHERE ws.winter_year BETWEEN 1986 AND 2026
GROUP BY ws.region
ORDER BY ws.region;


-- Query 5: Station-by-station detail for the snowfall comparison -
-- confirms whether the regional pattern is consistent across all
-- stations in that region, or driven by just one outlier station.
WITH winter_snowfall AS (
    SELECT
        sf.station_id,
        s.station_name,
        s.region,
        CASE
            WHEN EXTRACT(MONTH FROM sf.obs_date) <= 6
                THEN EXTRACT(YEAR FROM sf.obs_date)
            ELSE EXTRACT(YEAR FROM sf.obs_date) + 1
        END AS winter_year,
        SUM(sf.value_inches) AS total_snowfall
    FROM snowfall_daily sf
    JOIN stations s ON s.station_id = sf.station_id
    WHERE sf.datatype = 'SNOW'
      AND s.region IS NOT NULL
    GROUP BY sf.station_id, s.station_name, s.region, winter_year
)
SELECT
    ws.station_name,
    ws.region,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'El Nino'), 1) AS avg_snowfall_el_nino,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'La Nina'), 1) AS avg_snowfall_la_nina,
    ROUND(AVG(ws.total_snowfall) FILTER (WHERE o.enso_phase = 'Neutral'), 1) AS avg_snowfall_neutral
FROM winter_snowfall ws
JOIN enso_oni o ON o.winter_year = ws.winter_year
WHERE ws.winter_year BETWEEN 1986 AND 2026
GROUP BY ws.station_name, ws.region
ORDER BY ws.region, ws.station_name;
