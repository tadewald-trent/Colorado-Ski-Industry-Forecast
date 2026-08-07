"""
Extend the GHCND snowfall/precip pull back to 1950 (the start of the
official NOAA ONI record) for the 5 core stations that have SNOW data.
Vail Mountain and Wolf Creek Summit are excluded - they're SNOTEL-only
stations with no SNOW datatype (see data_dictionary.md), and the
SNOTEL network itself didn't exist before the late 1970s anyway.

This is the same fetch logic as scripts/fetch_ghcnd.py (v2, with
bounded retries and resume-by-skip), just scoped to a different year
range and station list, saving to a separate output folder so it
doesn't collide with the original 1986-2026 pull.

Usage:
    python3 scripts/fetch_ghcnd_extended.py
"""

import os
import time
import csv
import requests
from dotenv import load_dotenv

load_dotenv()
NOAA_TOKEN = os.getenv("NOAA_TOKEN")

if not NOAA_TOKEN:
    raise SystemExit(
        "No NOAA_TOKEN found. Check that .env exists in the project root "
        "and contains a line like: NOAA_TOKEN=your_token_here"
    )

STATIONS = {
    "breckenridge": "GHCND:USC00050909",
    "steamboat_springs": "GHCND:USC00057936",
    "winter_park": "GHCND:USC00059175",
    "telluride": "GHCND:USC00058204",
    "crested_butte": "GHCND:USC00051959",
}

START_YEAR = 1950
END_YEAR = 1985  # 1986 onward is already pulled

OUT_DIR = "data/raw/ghcnd_extended"
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

MAX_RETRIES = 3
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30


def log(msg):
    print(msg, flush=True)


def fetch_station_year(station_id, year):
    params = {
        "datasetid": "GHCND",
        "stationid": station_id,
        "datatypeid": "SNOW,PRCP",
        "startdate": f"{year}-01-01",
        "enddate": f"{year}-12-31",
        "units": "standard",
        "limit": 1000,
    }
    headers = {"token": NOAA_TOKEN}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                BASE_URL, params=params, headers=headers,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            )
            if response.status_code == 429:
                log(f"    Rate limited (attempt {attempt}/{MAX_RETRIES}), waiting 5s...")
                time.sleep(5)
                continue
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.RequestException as e:
            log(f"    Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            time.sleep(3)

    log(f"    Giving up on {station_id} {year} after {MAX_RETRIES} attempts")
    return []


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for name, station_id in STATIONS.items():
        out_path = os.path.join(OUT_DIR, f"{name}.csv")

        if os.path.exists(out_path):
            log(f"Skipping {name} - {out_path} already exists")
            continue

        log(f"Fetching {name} ({station_id}), {START_YEAR}-{END_YEAR}...")

        all_rows = []
        for year in range(START_YEAR, END_YEAR + 1):
            rows = fetch_station_year(station_id, year)
            all_rows.extend(rows)
            log(f"  {year}: {len(rows)} records")
            time.sleep(0.25)

        if not all_rows:
            log(f"  Note: no data returned for {name} in this range "
                f"(station may not have existed yet)")
            # Still write an empty file so the skip-logic works on rerun
            with open(out_path, "w", newline="") as f:
                f.write("date,datatype,station,attributes,value\n")
            continue

        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
            writer.writeheader()
            writer.writerows(all_rows)

        log(f"  Saved {len(all_rows)} rows to {out_path}\n")


if __name__ == "__main__":
    main()
