"""
WeatherPulse alerts.py — threshold checks -> weather_alert.

Pipeline stage 3. Reads fact_weather rows that have no alerts yet,
evaluates them against configured thresholds, and inserts matching
alerts. Alert types: EXTREME_HEAT, EXTREME_COLD, HIGH_WIND, HEAVY_PRECIPITATION.
"""

import logging

import psycopg2.extras
import yaml

from . import load

logger = logging.getLogger(__name__)

SEVERITY = "HIGH"
DEFAULT_CONFIG_PATH = "config/cities.yaml"


def load_thresholds(config_path=None):
    """Read alert thresholds from config/cities.yaml. Returns dict."""
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("alerts", {})


def evaluate(fact_row, thresholds):
    """Evaluate one fact_weather row against thresholds.
    Returns list[dict] of matching alerts (empty if none).
    Keys per alert: alert_type, message, triggered_value, threshold_value.
    """
    alerts = []

    temp = fact_row.get("temperature_c")
    wind = fact_row.get("wind_speed_kmh")
    precip = fact_row.get("precipitation_mm")

    temp_max = thresholds.get("temperature_max_c")
    temp_min = thresholds.get("temperature_min_c")
    wind_max = thresholds.get("wind_speed_max_kmh")
    precip_max = thresholds.get("precipitation_max_mm")

    if temp is not None and temp_max is not None and temp > temp_max:
        alerts.append({
            "alert_type": "EXTREME_HEAT",
            "message": f"Temperature {temp}°C exceeded max threshold {temp_max}°C",
            "triggered_value": temp,
            "threshold_value": temp_max,
        })

    if temp is not None and temp_min is not None and temp < temp_min:
        alerts.append({
            "alert_type": "EXTREME_COLD",
            "message": f"Temperature {temp}°C fell below min threshold {temp_min}°C",
            "triggered_value": temp,
            "threshold_value": temp_min,
        })

    if wind is not None and wind_max is not None and wind > wind_max:
        alerts.append({
            "alert_type": "HIGH_WIND",
            "message": f"Wind speed {wind}km/h exceeded threshold {wind_max}km/h",
            "triggered_value": wind,
            "threshold_value": wind_max,
        })

    if precip is not None and precip_max is not None and precip > precip_max:
        alerts.append({
            "alert_type": "HEAVY_PRECIPITATION",
            "message": f"Precipitation {precip}mm exceeded threshold {precip_max}mm",
            "triggered_value": precip,
            "threshold_value": precip_max,
        })

    return alerts


def get_new_facts(conn):
    """Return fact_weather rows that have no alerts yet."""
    query = """
        SELECT f.weather_id, f.city_id, f.observed_at, f.temperature_c,
               f.humidity_pct, f.wind_speed_kmh, f.wind_direction_deg,
               f.precipitation_mm, f.condition
        FROM fact_weather f
        LEFT JOIN weather_alert a ON f.weather_id = a.weather_id
        WHERE a.alert_id IS NULL
        ORDER BY f.weather_id;
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()


def run():
    """Main alerts entry point: evaluate new facts, insert matching alerts."""
    thresholds = load_thresholds()
    conn = load.get_connection()

    try:
        facts = get_new_facts(conn)
        logger.info("Evaluating %d fact_weather rows against thresholds", len(facts))

        for fact in facts:
            matched = evaluate(fact, thresholds)
            for alert in matched:
                load.insert_alert(
                    conn,
                    weather_id=fact["weather_id"],
                    city_id=fact["city_id"],
                    alert_type=alert["alert_type"],
                    severity=SEVERITY,
                    message=alert["message"],
                    triggered_value=alert["triggered_value"],
                    threshold_value=alert["threshold_value"],
                )
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()