"""
WeatherPulse extract.py — fetch weather from Open-Meteo, store in raw_weather.

Pipeline stage 1. For each configured city: upsert dim_city, call Open-Meteo,
insert the raw JSON response into raw_weather.
"""

import logging
import requests
import yaml

from . import load

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 15
CURRENT_PARAMS = "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weather_code"

DEFAULT_CONFIG_PATH = "config/cities.yaml"


def load_cities(config_path=None):
    """Read cities from config/cities.yaml. Returns list[dict]."""
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("cities", [])


def fetch_weather(city):
    """Call Open-Meteo for a single city. Returns (http_status, json_payload)."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "current": CURRENT_PARAMS,
        "timezone": "auto",
    }
    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
        return resp.status_code, resp.json()
    except requests.RequestException as e:
        logger.error("Request failed for %s, %s: %s", city.get("name"), city.get("country"), e)
        return None, {"error": str(e)}


def run():
    """Main extract entry point: load cities, fetch each, store raw."""
    cities = load_cities()
    conn = load.get_connection()

    try:
        for city in cities:
            city_id = load.upsert_city(
                conn,
                name=city["name"],
                country=city["country"],
                latitude=city["latitude"],
                longitude=city["longitude"],
            )

            status, payload = fetch_weather(city)

            raw_weather_id = load.insert_raw_weather(conn, city_id, status, payload)

            if status == 200:
                logger.info(
                    "Fetched %s, %s -> raw_weather_id=%s",
                    city["name"], city["country"], raw_weather_id,
                )
            else:
                logger.warning(
                    "Non-200 response for %s, %s (status=%s) -> raw_weather_id=%s",
                    city["name"], city["country"], status, raw_weather_id,
                )
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()