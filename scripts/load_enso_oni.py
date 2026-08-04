"""
Load the ENSO / Oceanic Nino Index (ONI) table: DJF (Dec-Jan-Feb) values
by winter year, 1950-2026, from NOAA's Climate Prediction Center.

Usage:
    python3 scripts/load_enso_oni.py
"""

import psycopg2

DB_NAME = "colorado_ski"

# DJF ONI values by winter_year (year of the Jan/Feb in that DJF season)
ONI_DJF = {
    1950: -1.5, 1951: -0.8, 1952: 0.5, 1953: 0.4, 1954: 0.8, 1955: -0.7,
    1956: -1.1, 1957: -0.2, 1958: 1.8, 1959: 0.6, 1960: -0.1, 1961: 0.0,
    1962: -0.2, 1963: -0.4, 1964: 1.1, 1965: -0.6, 1966: 1.4, 1967: -0.4,
    1968: -0.6, 1969: 1.1, 1970: 0.5, 1971: -1.4, 1972: -0.7, 1973: 1.8,
    1974: -1.8, 1975: -0.5, 1976: -1.6, 1977: 0.7, 1978: 0.7, 1979: 0.0,
    1980: 0.6, 1981: -0.3, 1982: 0.0, 1983: 2.2, 1984: -0.6, 1985: -1.0,
    1986: -0.5, 1987: 1.2, 1988: 0.8, 1989: -1.7, 1990: 0.1, 1991: 0.4,
    1992: 1.7, 1993: 0.1, 1994: 0.1, 1995: 1.0, 1996: -0.9, 1997: -0.5,
    1998: 2.2, 1999: -1.5, 2000: -1.7, 2001: -0.7, 2002: -0.1, 2003: 0.9,
    2004: 0.4, 2005: 0.6, 2006: -0.9, 2007: 0.7, 2008: -1.6, 2009: -0.8,
    2010: 1.5, 2011: -1.3, 2012: -0.7, 2013: -0.3, 2014: -0.3, 2015: 0.7,
    2016: 2.6, 2017: -0.2, 2018: -0.8, 2019: 0.9, 2020: 0.6, 2021: -0.9,
    2022: -0.8, 2023: -0.5, 2024: 1.9, 2025: -0.4, 2026: -0.4,
}


def phase(oni_value: float) -> str:
    if oni_value >= 0.5:
        return "El Nino"
    if oni_value <= -0.5:
        return "La Nina"
    return "Neutral"


def main():
    conn = psycopg2.connect(dbname=DB_NAME)
    cur = conn.cursor()

    for year, oni in ONI_DJF.items():
        cur.execute(
            """
            INSERT INTO enso_oni (winter_year, djf_oni, enso_phase)
            VALUES (%s, %s, %s)
            ON CONFLICT (winter_year) DO NOTHING
            """,
            (year, oni, phase(oni)),
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM enso_oni")
    total = cur.fetchone()[0]
    print(f"Done. enso_oni table now has {total} rows.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
