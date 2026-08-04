"""
Load the stations lookup table: the 7 core GHCND stations used for the
north/south snowfall comparison (RQ1), plus the 41 supplemental SNOTEL
stations pulled from those 7 stations' home counties.

Usage:
    python3 scripts/load_stations.py
"""

import psycopg2

DB_NAME = "colorado_ski"

# --- The 7 core GHCND stations -------------------------------------------
# (station_id, name, station_type, region, county, lat, lon, elev_ft, por_start, coverage_pct)
CORE_STATIONS = [
    ("GHCND:USC00050909", "Breckenridge",        "ghcnd_core", "north", "Summit",     39.48637, -106.04314, 9600,  "1893-01-01", 72.0),
    ("GHCND:USC00057936", "Steamboat Springs",    "ghcnd_core", "north", "Routt",      40.48830, -106.82330, 6867,  "1893-02-01", 90.0),
    ("GHCND:USC00059175", "Winter Park",          "ghcnd_core", "north", "Grand",      39.88767, -105.76126, 9124,  "1942-03-01", 98.0),
    ("GHCND:USS0006K39S", "Vail Mountain",        "snotel_core","north", "Eagle",      39.62000, -106.38000, 10300, "1978-09-30", 100.0),
    ("GHCND:USS0006M17S", "Wolf Creek Summit",    "snotel_core","south", "Mineral",    37.48000, -106.80000, 11000, "1986-08-20", 100.0),
    ("GHCND:USC00058204", "Telluride 4 WNW",      "ghcnd_core", "south", "San Miguel", 37.94930, -107.87360, 8646,  "1900-12-01", 89.0),
    ("GHCND:USC00051959", "Crested Butte",        "ghcnd_core", "south", "Gunnison",   38.87380, -106.97720, 8867,  "1909-06-01", 98.0),
]

# --- The 41 supplemental SNOTEL stations, by home county -----------------
# (triplet_id, name, county, elev_ft)
# Note: Vail Mountain and Wolf Creek Summit are already in CORE_STATIONS
# above (they're both core stations AND SNOTEL sites), so they're not
# repeated here.
SUPPLEMENTAL_SNOTEL = [
    # Summit County (Breckenridge)
    ("415", "Copper Mountain", "Summit", 10500),
    ("1120", "Elliot Ridge", "Summit", 10550),
    ("485", "Fremont Pass", "Summit", 11310),
    ("505", "Grizzly Peak", "Summit", 11110),
    ("531", "Hoosier Pass", "Summit", 11600),
    ("802", "Summit Ranch", "Summit", 9350),
    # Routt County (Steamboat Springs)
    ("1061", "Bear River", "Routt", 9100),
    ("457", "Dry Lake", "Routt", 8240),
    ("467", "Elk River", "Routt", 8710),
    ("1252", "Elkhead Divide", "Routt", 8780),
    ("940", "Lost Dog", "Routt", 9350),
    ("607", "Lynx Pass", "Routt", 8910),
    ("709", "Rabbit Ears", "Routt", 9390),
    ("825", "Tower", "Routt", 10610),
    # Grand County (Winter Park)
    ("1030", "Arapaho Ridge", "Grand", 10960),
    ("335", "Berthoud Summit", "Grand", 11300),
    ("913", "Buffalo Park", "Grand", 9240),
    ("1186", "Fool Creek", "Grand", 11130),
    ("1187", "High Lonesome", "Grand", 10630),
    ("970", "Jones Pass", "Grand", 10430),
    ("565", "Lake Irene", "Grand", 10680),
    ("1014", "Middle Fork Camp", "Grand", 8960),
    ("688", "Phantom Valley", "Grand", 9030),
    ("793", "Stillwater Creek", "Grand", 8760),
    ("869", "Willow Creek Pass", "Grand", 9520),
    # San Miguel County (Telluride)
    ("1344", "Alta Lakes", "San Miguel", 11290),
    ("589", "Lone Cone", "San Miguel", 9730),
    # Gunnison County (Crested Butte)
    ("380", "Butte", "Gunnison", 10190),
    ("618", "Mc Clure Pass", "Gunnison", 8760),
    ("669", "North Lost Trail", "Gunnison", 9190),
    ("680", "Park Cone", "Gunnison", 9600),
    ("701", "Porphyry Creek", "Gunnison", 10790),
    ("737", "Schofield Pass", "Gunnison", 10640),
    ("1141", "Upper Taylor", "Gunnison", 10710),
    # Eagle County (Vail)
    ("1041", "Beaver Ck Village", "Eagle", 8530),
    ("1040", "Mccoy Park", "Eagle", 9500),
    # Mineral County (Wolf Creek)
    ("624", "Middle Creek", "Mineral", 11260),
    ("1324", "Rat Creek", "Mineral", 11680),
    ("840", "Upper San Juan", "Mineral", 10140),
]


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    # Insert the 7 core stations
    for row in CORE_STATIONS:
        cur.execute(
            """
            INSERT INTO stations
                (station_id, station_name, station_type, region, county,
                 latitude, longitude, elevation_ft, period_of_record_start,
                 data_coverage_pct)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (station_id) DO NOTHING
            """,
            row,
        )

    # Insert the 41 supplemental SNOTEL stations
    for triplet_id, name, county, elev_ft in SUPPLEMENTAL_SNOTEL:
        station_id = f"SNOTEL:{triplet_id}"
        cur.execute(
            """
            INSERT INTO stations
                (station_id, station_name, station_type, region, county,
                 elevation_ft)
            VALUES (%s, %s, 'snotel_supplemental', NULL, %s, %s)
            ON CONFLICT (station_id) DO NOTHING
            """,
            (station_id, name, county, elev_ft),
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM stations")
    total = cur.fetchone()[0]
    print(f"Done. stations table now has {total} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
