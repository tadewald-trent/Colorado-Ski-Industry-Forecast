"""
Fetch daily snowfall (SNOW) and precipitation (PRCP) data for the 7 confirmed
GHCND stations, for the shared analysis window (1986-2026).

NOAA's CDO API caps GHCND requests at 1 year per call, so this script loops
over each station x each year and saves one raw CSV per station.

v2 improvements:
- Skips any station whose CSV already exists (safe to re-run after a
  partial/interrupted run - won't re-fetch Breckenridge/Steamboat, etc.)
- Bounded retries (max 3) instead of an unbounded retry loop that could
  hang indefinitely on a stuck request.
- Explicit connect/read timeouts and immediate print flushing so you can
  tell live progress from a genuine hang.

Usage:
    python3 scripts/fetch_ghcnd.py
"""

import os
import time
import csv
import requests
from dotenv import load_dotenv

# --- Config ---------------------------------------------------------------

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
    "vail_mountain": "GHCND:USS0006K39S",
    "wolf_creek_summit": "GHCND:USS0006M17S",
    "telluride": "GHCND:USC00058204",
    "crested_butte": "GHCND:USC00051959",
}

START_YEAR = 1986
END_YEAR = 2026  # inclusive

OUT_DIR = "data/raw/ghcnd"
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

MAX_RETRIES = 3
CONNECT_TIMEOUT = 10   # seconds to establish connection
READ_TIMEOUT = 30      # seconds to wait for a response after connecting


def log(msg: str):
    print(msg, flush=True)  # flush so output appears immediately, not buffered


def fetch_station_year(station_id: str, year: int) -> list[dict]:
    """Fetch one station's SNOW+PRCP daily records for one calendar year.
    Retries up to MAX_RETRIES times on failure, then gives up on this
    year (rather than hanging forever) and returns an empty list.
    """
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
                BASE_URL,
                params=params,
                headers=headers,
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

    log(f"    Giving up on {station_id} {year} after {MAX_RETRIES} attempts — skipping this year")
    return []


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for name, station_id in STATIONS.items():
        out_path = os.path.join(OUT_DIR, f"{name}.csv")

        if os.path.exists(out_path):
            log(f"Skipping {name} — {out_path} already exists")
            continue

        log(f"Fetching {name} ({station_id})...")

        all_rows = []
        for year in range(START_YEAR, END_YEAR + 1):
            rows = fetch_station_year(station_id, year)
            all_rows.extend(rows)
            log(f"  {year}: {len(rows)} records")
            time.sleep(0.25)

        if not all_rows:
            log(f"  WARNING: no data returned for {name} — check station ID/token")
            continue

        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
            writer.writeheader()
            writer.writerows(all_rows)

        log(f"  Saved {len(all_rows)} rows to {out_path}\n")


if __name__ == "__main__":
    main()
