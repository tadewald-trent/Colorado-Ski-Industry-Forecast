"""
Load daily snowfall (SNOW) and precipitation (PRCP) data from the 7
GHCND CSVs in data/raw/ghcnd/ into the snowfall_daily table.

Each CSV already has a 'station' column with the full GHCND ID
(e.g. 'GHCND:USC00050909'), which matches stations.station_id directly -
no filename-to-station mapping needed.

Usage:
    python3 scripts/load_snowfall_daily.py
"""

import csv
import glob
import os
import psycopg2
from psycopg2.extras import execute_values

DB_NAME = "colorado_ski"
RAW_DIR = "data/raw/ghcnd"


def read_csv_rows(path):
    """Read one station's CSV and yield (station_id, date, datatype, value, attributes) tuples."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_id = row["station"]
            obs_date = row["date"][:10]  # trim the "T00:00:00" suffix, keep YYYY-MM-DD
            datatype = row["datatype"]
            attributes = row["attributes"]

            # Value can be blank for missing readings - store as NULL, not 0
            raw_value = row["value"].strip()
            value = float(raw_value) if raw_value else None

            yield (station_id, obs_date, datatype, value, attributes)


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    csv_paths = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not csv_paths:
        raise SystemExit(f"No CSV files found in {RAW_DIR} — check the path.")

    total_rows = 0
    for path in csv_paths:
        station_name = os.path.basename(path).replace(".csv", "")
        rows = list(read_csv_rows(path))

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
    print(f"\nDone. Processed {total_rows} rows from {len(csv_paths)} files. "
          f"snowfall_daily table now has {db_total} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
