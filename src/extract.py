"""
WeatherPulse extract.py — fetch weather from Open-Meteo, store in raw_weather.

Pipeline stage 1. For each configured city: upsert dim_city, call Open-Meteo,
insert the raw JSON response into raw_weather.

NOTE: This is a stub skeleton. Implementation TODOs are marked inline.
"""

# TODO: import logging, requests, yaml
# TODO: from . import load

# TODO: OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
# TODO: REQUEST_TIMEOUT = 15
# TODO: CURRENT_PARAMS = "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weather_code"


def load_cities(config_path=None):
    """Read cities from config/cities.yaml. Returns list[dict]."""
    # TODO: open yaml, return config.get("cities", [])
    raise NotImplementedError


def fetch_weather(city):
    """Call Open-Meteo for a single city. Returns (http_status, json_payload)."""
    # TODO: requests.get(OPEN_METEO_URL, params={latitude, longitude, current, timezone}, timeout)
    # TODO: return resp.status_code, resp.json()
    raise NotImplementedError


def run():
    """Main extract entry point: load cities, fetch each, store raw."""
    # TODO: cities = load_cities()
    # TODO: conn = load.get_connection()
    # TODO: for city in cities:
    #           city_id = load.upsert_city(...)
    #           status, payload = fetch_weather(city)
    #           load.insert_raw_weather(conn, city_id, status, payload)
    # TODO: conn.close()
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: logging.basicConfig(...)
    run()