"""
WeatherPulse transform.py — raw_weather JSONB → structured fact_weather.

Pipeline stage 2. Reads unprocessed raw_weather rows, parses the JSONB
payload, maps WMO weather codes to condition text, upserts into fact_weather,
and marks the raw row as processed.

NOTE: This is a stub skeleton. Implementation TODOs are marked inline.
"""

# TODO: import logging
# TODO: from . import load

# TODO: WMO_CODES = {0: "Clear sky", 1: "Mainly clear", ...}   # WMO interpretation codes


def get_unprocessed(conn):
    """Return raw_weather rows where processed = FALSE."""
    # TODO: SELECT raw_weather_id, city_id, fetched_at, payload FROM raw_weather WHERE processed = FALSE
    raise NotImplementedError


def parse_payload(payload):
    """Extract current-weather fields from the Open-Meteo JSON payload.
    Returns dict with: temperature_c, humidity_pct, wind_speed_kmh,
    wind_direction_deg, precipitation_mm, weather_code, observed_at.
    """
    # TODO: read payload["current"][...] fields
    raise NotImplementedError


def transform_one(conn, raw_row):
    """Transform a single raw_weather row into fact_weather, then mark processed."""
    # TODO: parsed = parse_payload(payload)
    # TODO: condition = WMO_CODES.get(weather_code, ...)
    # TODO: load.upsert_fact_weather(...)
    # TODO: load.mark_raw_processed(conn, raw_id)
    raise NotImplementedError


def run():
    """Main transform entry point: process all unprocessed raw rows."""
    # TODO: conn = load.get_connection()
    # TODO: rows = get_unprocessed(conn)
    # TODO: for raw_row in rows: transform_one(conn, raw_row)
    # TODO: conn.close()
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: logging.basicConfig(...)
    run()