"""
Load SNOTEL SWE (snow water equivalent) data into snowpack_daily.

The source CSV is in WIDE format (one column per station, e.g.
"Alta Lakes (1344) Snow Water Equivalent (in) Start of Day Values").
This script reshapes it to LONG format (one row per station+date) to
match the rest of the schema, and maps each column to the correct
stations.station_id.

Two of the 41 SNOTEL stations (Vail Mountain #842, Wolf Creek Summit
#874) are also core GHCND stations, so they map to their GHCND id
rather than a 'SNOTEL:xxx' id - this keeps a single consistent
station_id per physical location across snowfall_daily and
snowpack_daily.

Usage:
    python3 scripts/load_snowpack_daily.py
"""

import csv
import re
import psycopg2
from psycopg2.extras import execute_values

DB_NAME = "colorado_ski"
CSV_PATH = "data/raw/snotel/snotel_swe_daily.csv"

# Triplet IDs that are also core GHCND stations - map to their GHCND id
# instead of a SNOTEL:xxx id, so there's one consistent station_id per
# physical location.
CORE_OVERLAP = {
    "842": "GHCND:USS0006K39S",  # Vail Mountain
    "874": "GHCND:USS0006M17S",  # Wolf Creek Summit
}


def find_header_row(path):
    """The CSV has a variable-length comment block (#...) before the
    real header row, which starts with 'Date,'. Return the line number
    (0-indexed) where the real header starts."""
    with open(path) as f:
        for i, line in enumerate(f):
            if line.startswith("Date,"):
                return i
    raise ValueError("Could not find header row starting with 'Date,'")


def parse_column_to_station_id(column_name):
    """Extract the triplet id from a column header like
    'Alta Lakes (1344) Snow Water Equivalent (in) Start of Day Values'
    and return the matching station_id."""
    match = re.search(r"\((\d+)\)", column_name)
    if not match:
        return None
    triplet_id = match.group(1)
    return CORE_OVERLAP.get(triplet_id, f"SNOTEL:{triplet_id}")


def main():
    header_line_num = find_header_row(CSV_PATH)

    with open(CSV_PATH, newline="") as f:
        for _ in range(header_line_num):
            next(f)  # skip the comment block
        reader = csv.DictReader(f)

        # Map each data column (all except 'Date') to a station_id
        column_to_station = {}
        for col in reader.fieldnames:
            if col == "Date":
                continue
            station_id = parse_column_to_station_id(col)
            if station_id:
                column_to_station[col] = station_id
            else:
                print(f"  WARNING: could not parse station from column: {col}")

        print(f"Mapped {len(column_to_station)} columns to stations.")

        # Reshape wide -> long
        long_rows = []
        for row in reader:
            obs_date = row["Date"]
            for col, station_id in column_to_station.items():
                raw_value = row[col].strip()
                if raw_value == "":
                    continue  # skip blanks - station wasn't operational yet, not a real zero
                long_rows.append((station_id, obs_date, float(raw_value)))

    print(f"Reshaped into {len(long_rows)} long-format rows. Loading into Postgres...")

    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    # Load in batches to keep memory/transaction size reasonable
    batch_size = 50000
    for i in range(0, len(long_rows), batch_size):
        batch = long_rows[i:i + batch_size]
        execute_values(
            cur,
            """
            INSERT INTO snowpack_daily (station_id, obs_date, swe_inches)
            VALUES %s
            ON CONFLICT (station_id, obs_date) DO NOTHING
            """,
            batch,
        )
        conn.commit()
        print(f"  Loaded batch {i // batch_size + 1} ({len(batch)} rows)")

    cur.execute("SELECT COUNT(*) FROM snowpack_daily")
    total = cur.fetchone()[0]
    print(f"\nDone. snowpack_daily table now has {total} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
