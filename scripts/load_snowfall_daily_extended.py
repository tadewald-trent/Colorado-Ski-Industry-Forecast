"""
Load the extended (1950-1985) GHCND snowfall/precip data from
data/raw/ghcnd_extended/ into the existing snowfall_daily table.

Same loading logic as scripts/load_snowfall_daily.py, just pointed at
the extended-range folder. Uses ON CONFLICT DO NOTHING, so it's safe
to run even if there's any accidental overlap with the original
1986-2026 data already in the table.

Usage:
    python3 scripts/load_snowfall_daily_extended.py
"""

import csv
import glob
import os
import psycopg2
from psycopg2.extras import execute_values

DB_NAME = "colorado_ski"
RAW_DIR = "data/raw/ghcnd_extended"


def read_csv_rows(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_id = row["station"]
            obs_date = row["date"][:10]
            datatype = row["datatype"]
            attributes = row["attributes"]
            raw_value = row["value"].strip()
            value = float(raw_value) if raw_value else None
            yield (station_id, obs_date, datatype, value, attributes)


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    csv_paths = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not csv_paths:
        raise SystemExit(f"No CSV files found in {RAW_DIR} - check the path.")

    total_rows = 0
    for path in csv_paths:
        station_name = os.path.basename(path).replace(".csv", "")
        rows = list(read_csv_rows(path))

        if not rows:
            print(f"  {station_name}: 0 rows (empty file, skipping)")
            continue

        execute_values(
            cur,
            """
            INSERT INTO snowfall_daily (station_id, obs_date, datatype, value_inches, attributes)
            VALUES %s
            ON CONFLICT (station_id, obs_date, datatype) DO NOTHING
            """,
            rows,
        )
        conn.commit()

        print(f"  {station_name}: loaded {len(rows)} rows")
        total_rows += len(rows)

    cur.execute("SELECT COUNT(*) FROM snowfall_daily")
    db_total = cur.fetchone()[0]
    print(f"\nDone. Processed {total_rows} extended rows from {len(csv_paths)} files. "
          f"snowfall_daily table now has {db_total} total rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
