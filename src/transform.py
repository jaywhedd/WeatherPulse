"""
WeatherPulse transform.py — raw_weather JSONB -> structured fact_weather.

Pipeline stage 2. Reads unprocessed raw_weather rows, parses the JSONB
payload, maps WMO weather codes to condition text, upserts into fact_weather,
and marks the raw row as processed.
"""

import logging

import psycopg2.extras

from . import load

logger = logging.getLogger(__name__)

# WMO weather interpretation codes (subset covering Open-Meteo's "weather_code")
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_unprocessed(conn):
    """Return raw_weather rows where processed = FALSE."""
    query = """
        SELECT raw_weather_id, city_id, fetched_at, payload
        FROM raw_weather
        WHERE processed = FALSE
        ORDER BY raw_weather_id;
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def parse_payload(payload):
    """Extract current-weather fields from the Open-Meteo JSON payload.
    Returns dict with: temperature_c, humidity_pct, wind_speed_kmh,
    wind_direction_deg, precipitation_mm, weather_code, observed_at.
    """
    current = payload.get("current", {})
    return {
        "observed_at": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "precipitation_mm": current.get("precipitation"),
        "weather_code": current.get("weather_code"),
    }


def transform_one(conn, raw_row):
    """Transform a single raw_weather row into fact_weather, then mark processed."""
    payload = raw_row["payload"]

    if not payload or "current" not in payload:
        logger.warning(
            "Skipping raw_weather_id=%s — no usable payload (likely a failed API call)",
            raw_row["raw_weather_id"],
        )
        load.mark_raw_processed(conn, raw_row["raw_weather_id"])
        return None

    parsed = parse_payload(payload)

    if parsed["observed_at"] is None:
        logger.warning(
            "Skipping raw_weather_id=%s — missing observed_at in payload",
            raw_row["raw_weather_id"],
        )
        load.mark_raw_processed(conn, raw_row["raw_weather_id"])
        return None

    condition = WMO_CODES.get(parsed["weather_code"], "Unknown")

    weather_id = load.upsert_fact_weather(
        conn,
        city_id=raw_row["city_id"],
        observed_at=parsed["observed_at"],
        temperature_c=parsed["temperature_c"],
        humidity_pct=parsed["humidity_pct"],
        wind_speed_kmh=parsed["wind_speed_kmh"],
        wind_direction_deg=parsed["wind_direction_deg"],
        precipitation_mm=parsed["precipitation_mm"],
        condition=condition,
        raw_weather_id=raw_row["raw_weather_id"],
    )

    load.mark_raw_processed(conn, raw_row["raw_weather_id"])

    logger.info(
        "Transformed raw_weather_id=%s -> weather_id=%s (%s)",
        raw_row["raw_weather_id"], weather_id, condition,
    )
    return weather_id


def run():
    """Main transform entry point: process all unprocessed raw rows."""
    conn = load.get_connection()
    try:
        rows = get_unprocessed(conn)
        logger.info("Found %d unprocessed raw_weather rows", len(rows))
        for raw_row in rows:
            transform_one(conn, raw_row)
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()