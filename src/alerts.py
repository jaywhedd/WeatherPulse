"""
WeatherPulse alerts.py — threshold checks → weather_alert.

Pipeline stage 3. Reads fact_weather rows that have no alerts yet,
evaluates them against configured thresholds, and inserts matching
alerts. Alert types: EXTREME_HEAT, EXTREME_COLD, HIGH_WIND, HEAVY_PRECIPITATION.

NOTE: This is a stub skeleton. Implementation TODOs are marked inline.
"""

# TODO: import logging, yaml
# TODO: from . import load

# TODO: SEVERITY = "HIGH"


def load_thresholds(config_path=None):
    """Read alert thresholds from config/cities.yaml. Returns dict."""
    # TODO: open yaml, return config.get("alerts", {})
    raise NotImplementedError


def evaluate(fact_row, thresholds):
    """Evaluate one fact_weather row against thresholds.
    Returns list[dict] of matching alerts (empty if none).
    Keys per alert: alert_type, message, triggered_value, threshold_value.
    """
    # TODO: check temperature_c > temperature_max_c -> EXTREME_HEAT
    # TODO: check temperature_c < temperature_min_c -> EXTREME_COLD
    # TODO: check wind_speed_kmh > wind_speed_max_kmh -> HIGH_WIND
    # TODO: check precipitation_mm > precipitation_max_mm -> HEAVY_PRECIPITATION
    raise NotImplementedError


def get_new_facts(conn):
    """Return fact_weather rows that have no alerts yet."""
    # TODO: SELECT f.* FROM fact_weather f LEFT JOIN weather_alert a ON f.weather_id = a.weather_id
    #       WHERE a.alert_id IS NULL
    raise NotImplementedError


def run():
    """Main alerts entry point: evaluate new facts, insert matching alerts."""
    # TODO: thresholds = load_thresholds()
    # TODO: conn = load.get_connection()
    # TODO: facts = get_new_facts(conn)
    # TODO: for fact in facts:
    #           matched = evaluate(fact, thresholds)
    #           for alert in matched: load.insert_alert(...)
    # TODO: conn.close()
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: logging.basicConfig(...)
    run()