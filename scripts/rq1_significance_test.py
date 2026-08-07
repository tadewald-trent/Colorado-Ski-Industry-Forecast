"""
Improvement 3 for RQ1: run a proper statistical test (independent
samples t-test) on the El Nino vs. La Nina snowpack difference, instead
of just comparing raw averages. This tells us whether the differences
seen in rq1_enso_snowpack.sql are likely to be a real pattern or could
easily be due to chance given the sample size.

A p-value < 0.05 is the conventional (though somewhat arbitrary)
threshold for "statistically significant" - i.e., a difference this
large would be unlikely to occur by chance alone if there were truly
no underlying effect.

Usage:
    python3 scripts/rq1_significance_test.py
"""

import psycopg2
from scipy import stats

DB_NAME = "colorado_ski"


def get_peak_swe_by_phase(cur, region, phase):
    """Return a list of peak-SWE values (one per station-winter) for
    the given region and ENSO phase, using all stations with a region
    assigned."""
    cur.execute(
        """
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
            WHERE s.region = %s
            GROUP BY sp.station_id, s.region, winter_year
        )
        SELECT wps.peak_swe
        FROM winter_peak_swe wps
        JOIN enso_oni o ON o.winter_year = wps.winter_year
        WHERE o.enso_phase = %s
          AND wps.winter_year BETWEEN 1986 AND 2026
        """,
        (region, phase),
    )
    return [float(row[0]) for row in cur.fetchall() if row[0] is not None]


def run_test(region, el_nino_values, la_nina_values):
    n_el_nino = len(el_nino_values)
    n_la_nina = len(la_nina_values)

    t_stat, p_value = stats.ttest_ind(el_nino_values, la_nina_values, equal_var=False)

    print(f"\n--- {region.upper()} ---")
    print(f"  El Nino: n={n_el_nino}, mean={sum(el_nino_values)/n_el_nino:.2f}\"")
    print(f"  La Nina: n={n_la_nina}, mean={sum(la_nina_values)/n_la_nina:.2f}\"")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {p_value:.4f}")
    if p_value < 0.05:
        print("  -> Statistically significant at the p<0.05 level.")
    else:
        print("  -> NOT statistically significant at the p<0.05 level.")
        print("     (Could plausibly be due to chance given this sample size.)")


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    print("RQ1 significance test: El Nino vs. La Nina peak SWE, by region")
    print("Using all stations with an assigned region (46 stations total).")

    for region in ["north", "south"]:
        el_nino = get_peak_swe_by_phase(cur, region, "El Nino")
        la_nina = get_peak_swe_by_phase(cur, region, "La Nina")
        run_test(region, el_nino, la_nina)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
