"""
WeatherPulse load.py — PostgreSQL connection and upsert helpers.

Responsibilities:
  - Open a psycopg2 connection from POSTGRES_* env vars.
  - Provide a generic upsert helper.
  - Provide table-specific insert/upsert helpers used by the other stages.

NOTE: This is a stub skeleton. Implementation TODOs are marked inline.
"""

# TODO: import os, logging, psycopg2, psycopg2.extras


def get_connection():
    """Return a psycopg2 connection using POSTGRES_* env vars.

    Reads: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    """
    # TODO: implement using psycopg2.connect(...)
    raise NotImplementedError


def upsert(conn, table, columns, values, conflict_cols):
    """Generic INSERT ... ON CONFLICT DO UPDATE, returning the row id.

    Parameters
    ----------
    conn : psycopg2 connection
    table : str
    columns : list[str]
    values : tuple
    conflict_cols : list[str]   columns forming the unique constraint
    """
    # TODO: build INSERT ... ON CONFLICT (...) DO UPDATE SET ... RETURNING <table>_id
    raise NotImplementedError


def upsert_city(conn, name, country, latitude, longitude):
    """Insert or return existing dim_city row. Conflict on (name, country)."""
    # TODO: call upsert(...) with dim_city columns
    raise NotImplementedError


def insert_raw_weather(conn, city_id, http_status, payload):
    """Insert a raw API response into raw_weather. Returns raw_weather_id."""
    # TODO: INSERT into raw_weather (city_id, http_status, payload) RETURNING raw_weather_id
    raise NotImplementedError


def upsert_fact_weather(conn, city_id, observed_at, temperature_c,
                        humidity_pct, wind_speed_kmh, wind_direction_deg,
                        precipitation_mm, condition, raw_weather_id):
    """Upsert into fact_weather. Conflict on (city_id, observed_at)."""
    # TODO: call upsert(...) with fact_weather columns
    raise NotImplementedError


def insert_alert(conn, weather_id, city_id, alert_type, severity, message,
                triggered_value, threshold_value):
    """Insert a weather_alert row (ON CONFLICT DO NOTHING)."""
    # TODO: INSERT into weather_alert (...) ON CONFLICT (weather_id, alert_type) DO NOTHING
    raise NotImplementedError


def mark_raw_processed(conn, raw_weather_id):
    """Flag a raw_weather row as processed=TRUE, processed_at=now()."""
    # TODO: UPDATE raw_weather SET processed=TRUE, processed_at=now() WHERE raw_weather_id=%s
    raise NotImplementedError