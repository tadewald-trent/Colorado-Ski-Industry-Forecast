"""
RQ2 significance testing: does the snow index predict skier visits?

Tests run:
  1. All 12 comparable seasons pooled (1983-2026) - acknowledging this
     mixes eras of very different industry size/maturity, a real
     confound separate from snow itself.
  2. Just the 7 seasons in the epic_and_ikon era (2019-2026) - the
     most methodologically consistent, modern subset, though an even
     smaller sample.

Usage:
    python3 scripts/rq2_significance_test.py
"""

import psycopg2
from scipy import stats

DB_NAME = "colorado_ski"


def get_snow_and_visits(cur, era_filter=None):
    query = """
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
            SELECT winter_year, AVG(station_total_snowfall) AS avg_snowfall_index
            FROM winter_snowfall
            GROUP BY winter_year
        )
        SELECT si.avg_snowfall_index, v.visits, v.winter_year
        FROM skier_visits v
        JOIN snow_index si ON si.winter_year = v.winter_year
        WHERE v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
        ORDER BY v.winter_year
    """
    cur.execute(query)
    rows = cur.fetchall()

    if era_filter == "epic_and_ikon":
        rows = [r for r in rows if r[2] >= 2019]

    snow = [float(r[0]) for r in rows]
    visits = [float(r[1]) for r in rows]
    return snow, visits


def run_regression(label, snow_values, visit_values):
    result = stats.linregress(snow_values, visit_values)
    r_squared = result.rvalue ** 2

    print(f"\n--- {label} ---")
    print(f"  n = {len(snow_values)}")
    print(f"  slope: {result.slope:.1f} (change in visits per 1-inch increase in snow index)")
    print(f"  r-value (correlation): {result.rvalue:.3f}")
    print(f"  r-squared: {r_squared:.4f} ({r_squared*100:.1f}% of variance in visits explained by snow)")
    print(f"  p-value: {result.pvalue:.4f}")
    if result.pvalue < 0.05:
        print("  -> Statistically significant relationship at p<0.05.")
    else:
        print("  -> NOT statistically significant at p<0.05.")
        print("     (Small sample size - interpret with real caution either way.)")


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    print("RQ2: snow index vs. skier visits")

    snow_all, visits_all = get_snow_and_visits(cur)
    run_regression("All 12 comparable seasons, 1983-2026 (pooled, mixes industry eras)",
                    snow_all, visits_all)

    snow_modern, visits_modern = get_snow_and_visits(cur, era_filter="epic_and_ikon")
    run_regression("Epic+Ikon era only, 2019-2026 (most consistent subset)",
                    snow_modern, visits_modern)

    # Sensitivity check: is the 2019-2026 result driven mainly by the
    # extreme 2025-26 season (lowest snow AND lowest visits by far)?
    # Re-run with that season excluded to check robustness.
    snow_no2026 = snow_modern[:-1]  # relies on winter_year ASC order from the query
    visits_no2026 = visits_modern[:-1]
    run_regression("Epic+Ikon era, EXCLUDING 2025-26 (sensitivity check)",
                    snow_no2026, visits_no2026)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
