"""
RQ3 significance testing: does Colorado skier-visit volume predict
Vail Resorts revenue?

IMPORTANT SCOPE LIMITATION: Vail Resorts operates resorts outside
Colorado (Whistler Blackcomb, Park City, Midwest/Northeast properties,
etc.), while skier_visits is Colorado statewide only. This test can
only speak to whether Colorado visitation correlates with total
company revenue, not Colorado-specific revenue.

Only 8 fiscal years have both a Vail revenue figure and a comparable
Colorado skier-visits figure: 2010, 2014, 2019, 2021-2025. This is a
very small sample - results here should be treated as exploratory,
not confirmatory.

Tests run:
  1. All 8 overlapping years.
  2. The 7 years excluding FY2019, which was itself an acquisition
     year (Crested Butte, Okemo, Mount Sunapee, Stevens Pass) - since
     that year's revenue jump partly reflects new properties, not
     visits/weather.

Usage:
    python3 scripts/rq3_significance_test.py
"""

import psycopg2
from scipy import stats

DB_NAME = "colorado_ski"


def get_visits_and_revenue(cur, exclude_acquisition_years=False):
    query = """
        SELECT v.visits, r.revenue_millions, r.is_acquisition_year, r.fiscal_year
        FROM vail_revenue r
        JOIN skier_visits v
            ON v.winter_year = r.fiscal_year
            AND v.measurement_basis IN ('resort_level_sum', 'full_state_estimate')
        ORDER BY r.fiscal_year
    """
    cur.execute(query)
    rows = cur.fetchall()

    if exclude_acquisition_years:
        rows = [r for r in rows if not r[2]]

    visits = [float(r[0]) for r in rows]
    revenue = [float(r[1]) for r in rows]
    years = [r[3] for r in rows]
    return visits, revenue, years


def run_regression(label, visits, revenue, years):
    result = stats.linregress(visits, revenue)
    r_squared = result.rvalue ** 2

    print(f"\n--- {label} ---")
    print(f"  n = {len(visits)}  (years: {years})")
    print(f"  slope: {result.slope:.6f} ($M revenue per additional visit)")
    print(f"  r-value (correlation): {result.rvalue:.3f}")
    print(f"  r-squared: {r_squared:.4f} ({r_squared*100:.1f}% of variance in revenue explained by visits)")
    print(f"  p-value: {result.pvalue:.4f}")
    if result.pvalue < 0.05:
        print("  -> Statistically significant relationship at p<0.05.")
    else:
        print("  -> NOT statistically significant at p<0.05.")
        print("     (Very small sample size - interpret with real caution.)")


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    print("RQ3: Colorado skier visits vs. Vail Resorts total revenue")
    print("NOTE: Vail Resorts revenue includes non-Colorado properties.")

    visits_all, revenue_all, years_all = get_visits_and_revenue(cur)
    run_regression("All 8 overlapping years", visits_all, revenue_all, years_all)

    visits_clean, revenue_clean, years_clean = get_visits_and_revenue(
        cur, exclude_acquisition_years=True
    )
    run_regression("7 years, excluding FY2019 acquisition year",
                    visits_clean, revenue_clean, years_clean)

    # Sensitivity check: 2010 and 2014 have much lower revenue than
    # the 2021-2025 cluster. Check whether the relationship is a real
    # graded pattern, or just an artifact of two separated groups
    # (old-low vs recent-high) rather than a smooth trend.
    recent_idx = [i for i, y in enumerate(years_clean) if y >= 2021]
    visits_recent = [visits_clean[i] for i in recent_idx]
    revenue_recent = [revenue_clean[i] for i in recent_idx]
    years_recent = [years_clean[i] for i in recent_idx]
    run_regression("Recent cluster only, 2021-2025 (rules out old-vs-new illusion)",
                    visits_recent, revenue_recent, years_recent)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
