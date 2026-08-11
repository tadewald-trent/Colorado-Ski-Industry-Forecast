"""
Export the key datasets needed for the Tableau Public dashboard, since
Tableau Public cannot connect directly to a local PostgreSQL database
(a Tableau Desktop/paid-tier feature only). This script runs the same
underlying queries used in the RQ1-RQ4 analysis and writes clean CSVs
to dashboard/data/, ready to load into Tableau Public.

Usage:
    python3 scripts/export_dashboard_data.py
"""

import csv
import os
import psycopg2

DB_NAME = "colorado_ski"
OUT_DIR = "dashboard/data"


def export_query(cur, query, filename, params=None):
    cur.execute(query, params or ())
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"  {filename}: {len(rows)} rows")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    print("Exporting dashboard data...")

    # RQ1: SNOTEL peak SWE by region and ENSO phase (46 stations, full history)
    export_query(cur, """
        WITH winter_peak_swe AS (
            SELECT
                sp.station_id, s.region,
                CASE WHEN EXTRACT(MONTH FROM sp.obs_date) <= 6
                     THEN EXTRACT(YEAR FROM sp.obs_date)
                     ELSE EXTRACT(YEAR FROM sp.obs_date) + 1 END AS winter_year,
                MAX(sp.swe_inches) AS peak_swe
            FROM snowpack_daily sp
            JOIN stations s ON s.station_id = sp.station_id
            WHERE s.region IS NOT NULL
            GROUP BY sp.station_id, s.region, winter_year
        )
        SELECT wps.region, o.enso_phase,
               ROUND(AVG(wps.peak_swe), 2) AS avg_peak_swe,
               COUNT(*) AS n
        FROM winter_peak_swe wps
        JOIN enso_oni o ON o.winter_year = wps.winter_year
        GROUP BY wps.region, o.enso_phase
        ORDER BY wps.region, o.enso_phase
    """, "rq1_swe_by_phase_region.csv")

    # RQ2: snow index vs visits, comparable seasons only, with pass era
    export_query(cur, """
        WITH winter_snowfall AS (
            SELECT
                CASE WHEN EXTRACT(MONTH FROM sf.obs_date) <= 6
                     THEN EXTRACT(YEAR FROM sf.obs_date)
                     ELSE EXTRACT(YEAR FROM sf.obs_date) + 1 END AS winter_year,
                sf.station_id,
                SUM(sf.value_inches) AS station_total_snowfall
            FROM snowfall_daily sf
            JOIN stations s ON s.station_id = sf.station_id
            WHERE sf.datatype = 'SNOW' AND s.region IS NOT NULL
            GROUP BY winter_year, sf.station_id
        ),
        snow_index AS (
            SELECT winter_year, ROUND(AVG(station_total_snowfall), 1) AS avg_snowfall_index
            FROM winter_snowfall GROUP BY winter_year
        )
        SELECT
            v.season_label, v.winter_year, v.visits, si.avg_snowfall_index,
            CASE
                WHEN v.winter_year < 2009 THEN 'pre_epic'
                WHEN v.winter_year < 2019 THEN 'epic_only'
                ELSE 'epic_and_ikon'
            END AS pass_era
        FROM skier_visits v
        JOIN snow_index si ON si.winter_year = v.winter_year
        WHERE v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
        ORDER BY v.winter_year
    """, "rq2_snow_vs_visits.csv")

    # RQ3: visits vs Vail Resorts revenue, with acquisition flag
    export_query(cur, """
        SELECT
            r.fiscal_year, r.revenue_millions, r.is_acquisition_year,
            r.acquisition_note, v.visits AS co_skier_visits
        FROM vail_revenue r
        JOIN skier_visits v
            ON v.winter_year = r.fiscal_year
            AND v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
        ORDER BY r.fiscal_year
    """, "rq3_visits_vs_revenue.csv")

    cur.close()
    conn.close()
    print("\nDone. CSVs saved to dashboard/data/")


if __name__ == "__main__":
    main()
