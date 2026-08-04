"""
Load Vail Resorts fiscal-year revenue (FY ends July 31), FY2009-FY2025,
with is_acquisition_year flagged for years when a major acquisition
closed - see data_dictionary.md for the full acquisition timeline and
sourcing.

Usage:
    python3 scripts/load_vail_revenue.py
"""

import psycopg2

DB_NAME = "colorado_ski"

# (fiscal_year, revenue_millions, is_acquisition_year, acquisition_note, source)
VAIL_REVENUE = [
    (2009, 1004, False, None, "Vail Resorts 10-K / investor releases"),
    (2010, 895,  False, None, "Vail Resorts 10-K / investor releases"),
    (2011, 1167, False, None, "Vail Resorts 10-K / investor releases"),
    (2012, 1024, False, None, "Vail Resorts 10-K / investor releases"),
    (2013, 1121, False, None, "Vail Resorts 10-K / investor releases"),
    (2014, 1255, False, None, "Vail Resorts 10-K / investor releases"),
    (2015, 1400, False, None, "Vail Resorts 10-K / investor releases"),
    (2016, 1601, False, None, "Vail Resorts 10-K / investor releases"),
    (2017, 1907, True,  "Whistler Blackcomb acquisition closed Oct 2016 ($1.1B)",
     "Vail Resorts 10-K / investor releases"),
    (2018, 2012, False, None, "Vail Resorts 10-K / investor releases"),
    (2019, 2272, True,  "Crested Butte, Okemo, Mount Sunapee, Stevens Pass acquired 2018-19",
     "Vail Resorts 10-K / investor releases"),
    (2020, 1964, True,  "Peak Resorts (17 US ski areas) acquired fall 2019",
     "Vail Resorts 10-K / investor releases"),
    (2021, 1910, False, None, "Vail Resorts 10-K / investor releases"),
    (2022, 2526, False, None, "Vail Resorts 10-K / investor releases"),
    (2023, 2889, False, None, "Vail Resorts 10-K / investor releases"),
    (2024, 2885, False, None, "Vail Resorts 10-K / investor releases"),
    (2025, 2958, False, None, "Vail Resorts 10-K / investor releases"),
]


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    for row in VAIL_REVENUE:
        cur.execute(
            """
            INSERT INTO vail_revenue
                (fiscal_year, revenue_millions, is_acquisition_year, acquisition_note, source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (fiscal_year) DO NOTHING
            """,
            row,
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM vail_revenue")
    total = cur.fetchone()[0]
    print(f"Done. vail_revenue table now has {total} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
