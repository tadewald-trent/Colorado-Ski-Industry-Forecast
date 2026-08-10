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
        """,
        (region, phase),
    )
    return [float(row[0]) for row in cur.fetchall() if row[0] is not None]


def get_peak_swe_with_oni(cur, region):
    """Return parallel lists (oni_values, swe_values) for every
    station-winter in the given region, using the continuous ONI value
    rather than a categorical phase - for regression."""
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
        SELECT o.djf_oni, wps.peak_swe
        FROM winter_peak_swe wps
        JOIN enso_oni o ON o.winter_year = wps.winter_year
        WHERE wps.peak_swe IS NOT NULL
        """,
        (region,),
    )
    rows = cur.fetchall()
    return [float(r[0]) for r in rows], [float(r[1]) for r in rows]


def get_seasonal_snowfall_with_oni(cur, region):
    """Same as above, but for GHCND total seasonal snowfall."""
    cur.execute(
        """
        WITH winter_snowfall AS (
            SELECT
                sf.station_id,
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
              AND s.region = %s
            GROUP BY sf.station_id, s.region, winter_year
        )
        SELECT o.djf_oni, ws.total_snowfall
        FROM winter_snowfall ws
        JOIN enso_oni o ON o.winter_year = ws.winter_year
        WHERE ws.total_snowfall IS NOT NULL
        """,
        (region,),
    )
    rows = cur.fetchall()
    return [float(r[0]) for r in rows], [float(r[1]) for r in rows]


def run_regression(region, oni_values, outcome_values, metric_label):
    result = stats.linregress(oni_values, outcome_values)
    r_squared = result.rvalue ** 2

    print(f"\n--- {region.upper()} ({metric_label}) ---")
    print(f"  n = {len(oni_values)}")
    print(f"  slope: {result.slope:.3f} (change in {metric_label} per 1-unit ONI increase)")
    print(f"  r-value (correlation): {result.rvalue:.3f}")
    print(f"  r-squared: {r_squared:.4f} ({r_squared*100:.1f}% of variance explained by ONI)")
    print(f"  p-value: {result.pvalue:.4f}")
    if result.pvalue < 0.05:
        print("  -> Statistically significant linear relationship at p<0.05.")
    else:
        print("  -> NOT a statistically significant linear relationship at p<0.05.")


def run_test(region, el_nino_values, la_nina_values, metric_label):
    n_el_nino = len(el_nino_values)
    n_la_nina = len(la_nina_values)

    t_stat, p_value = stats.ttest_ind(el_nino_values, la_nina_values, equal_var=False)

    print(f"\n--- {region.upper()} ({metric_label}) ---")
    print(f"  El Nino: n={n_el_nino}, mean={sum(el_nino_values)/n_el_nino:.2f}\"")
    print(f"  La Nina: n={n_la_nina}, mean={sum(la_nina_values)/n_la_nina:.2f}\"")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {p_value:.4f}")
    if p_value < 0.05:
        print("  -> Statistically significant at the p<0.05 level.")
    else:
        print("  -> NOT statistically significant at the p<0.05 level.")
        print("     (Could plausibly be due to chance given this sample size.)")


def get_seasonal_snowfall_by_phase(cur, region, phase):
    """Return a list of total-seasonal-snowfall values (one per
    station-winter) for the given region and ENSO phase, using GHCND
    SNOW data and each station's full available history (back to
    1950, the start of the ENSO/ONI record)."""
    cur.execute(
        """
        WITH winter_snowfall AS (
            SELECT
                sf.station_id,
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
              AND s.region = %s
            GROUP BY sf.station_id, s.region, winter_year
        )
        SELECT ws.total_snowfall
        FROM winter_snowfall ws
        JOIN enso_oni o ON o.winter_year = ws.winter_year
        WHERE o.enso_phase = %s
        """,
        (region, phase),
    )
    return [float(row[0]) for row in cur.fetchall() if row[0] is not None]


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    print("=" * 60)
    print("TEST 1: SNOTEL peak SWE, El Nino vs. La Nina, by region")
    print("Using all 46 stations with an assigned region.")
    print("=" * 60)

    for region in ["north", "south"]:
        el_nino = get_peak_swe_by_phase(cur, region, "El Nino")
        la_nina = get_peak_swe_by_phase(cur, region, "La Nina")
        run_test(region, el_nino, la_nina, "peak SWE")

    print("\n" + "=" * 60)
    print("TEST 2: GHCND total seasonal snowfall, El Nino vs. La Nina, by region")
    print("Using 5 stations with SNOW data, full history back to 1950.")
    print("=" * 60)

    for region in ["north", "south"]:
        el_nino = get_seasonal_snowfall_by_phase(cur, region, "El Nino")
        la_nina = get_seasonal_snowfall_by_phase(cur, region, "La Nina")
        run_test(region, el_nino, la_nina, "total snowfall")

    print("\n" + "=" * 60)
    print("TEST 3: Linear regression, continuous ONI vs. peak SWE, by region")
    print("Uses actual ONI magnitude rather than El Nino/La Nina/Neutral categories.")
    print("=" * 60)

    for region in ["north", "south"]:
        oni_vals, swe_vals = get_peak_swe_with_oni(cur, region)
        run_regression(region, oni_vals, swe_vals, "peak SWE")

    print("\n" + "=" * 60)
    print("TEST 4: Linear regression, continuous ONI vs. total seasonal snowfall, by region")
    print("=" * 60)

    for region in ["north", "south"]:
        oni_vals, snow_vals = get_seasonal_snowfall_with_oni(cur, region)
        run_regression(region, oni_vals, snow_vals, "total snowfall")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
