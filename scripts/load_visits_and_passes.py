"""
Load pass_launches (Epic Pass, Ikon Pass) and skier_visits (CSCUSA
statewide totals 2013-2026, plus pre-2010 analog-year totals computed
from Storm Skiing's per-resort data).

Usage:
    python3 scripts/load_visits_and_passes.py
"""

import psycopg2

DB_NAME = "colorado_ski"

PASS_LAUNCHES = [
    # (pass_name, launch_year, launch_price, notes)
    ("Epic Pass", 2008, 579.00,
     "Launched March 2008 for the 2008-09 season; initially covered Vail, "
     "Breckenridge, Beaver Creek, Keystone, and Heavenly. Replaced an "
     "$1,850 Vail+Beaver Creek-only pass."),
    ("Ikon Pass", 2018, 899.00,
     "Launched by Alterra Mountain Company for the 2018-19 season."),
]

# (season_label, winter_year, visits, measurement_basis, is_complete, source)
SKIER_VISITS = [
    # Pre-2010 analog years (resort-level sums from Storm Skiing data)
    ("1982-83",    1983, 8078362,  "resort_level_sum",     True,  "Storm Skiing per-resort data, summed"),
    ("1997-98",    1998, 11941777, "resort_level_sum",     True,  "Storm Skiing per-resort data, summed"),
    ("1999-2000",  2000, 10861892, "resort_level_sum",     True,  "Storm Skiing per-resort data, summed"),
    ("2009-10",    2010, 11857879, "resort_level_sum",     True,  "Storm Skiing per-resort data, summed"),
    # CSCUSA-reported statewide figures, 2013-14 through 2025-26
    ("2013-14",    2014, 12600000, "full_state_estimate",  True,  "CSCUSA (last year Vail Resorts disclosed)"),
    ("2013-14",    2014, 7100000,  "cscusa_members_only",  True,  "CSCUSA (alt. metric, same season)"),
    ("2014-15",    2015, 7100000,  "cscusa_members_only",  True,  "CSCUSA"),
    ("2015-16",    2016, 7400000,  "cscusa_members_only",  True,  "CSCUSA (record for this metric)"),
    ("2016-17",    2017, 7300000,  "cscusa_members_only",  True,  "CSCUSA"),
    ("2017-18",    2018, 7100000,  "cscusa_members_only",  True,  "CSCUSA"),
    ("2018-19",    2019, 13800000, "full_state_estimate",  True,  "CSCUSA (methodology switch point)"),
    ("2020-21",    2021, 12000000, "full_state_estimate",  True,  "CSCUSA"),
    ("2021-22",    2022, 13900000, "full_state_estimate",  True,  "CSCUSA"),
    ("2022-23",    2023, 14800000, "full_state_estimate",  True,  "CSCUSA (all-time record)"),
    ("2023-24",    2024, 14000000, "full_state_estimate",  True,  "CSCUSA"),
    ("2024-25",    2025, 13800000, "full_state_estimate",  True,  "CSCUSA"),
    ("2025-26",    2026, 10500000, "full_state_estimate",  True,  "CSCUSA (24% drop, worst since 1991-92)"),
]


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    for row in PASS_LAUNCHES:
        cur.execute(
            """
            INSERT INTO pass_launches (pass_name, launch_year, launch_price, notes)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (pass_name) DO NOTHING
            """,
            row,
        )

    for row in SKIER_VISITS:
        cur.execute(
            """
            INSERT INTO skier_visits
                (season_label, winter_year, visits, measurement_basis, is_complete, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (winter_year, measurement_basis) DO NOTHING
            """,
            row,
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM pass_launches")
    pass_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM skier_visits")
    visits_count = cur.fetchone()[0]

    print(f"Done. pass_launches has {pass_count} rows, skier_visits has {visits_count} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
