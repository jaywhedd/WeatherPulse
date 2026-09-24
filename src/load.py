"""
WeatherPulse load.py — PostgreSQL connection and upsert helpers.
 
Responsibilities:
  - Open a psycopg2 connection from POSTGRES_* env vars.
  - Provide a generic upsert helper.
  - Provide table-specific insert/upsert helpers used by the other stages.
"""
 
import os
import logging
import psycopg2
import psycopg2.extras
 
logger = logging.getLogger(__name__)
 
 
def get_connection():
    """Return a psycopg2 connection using POSTGRES_* env vars.
 
    Reads: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "weatherpulse"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        logger.info("Connected to Postgres at %s", os.getenv("POSTGRES_HOST", "localhost"))
        return conn
    except psycopg2.OperationalError as e:
        logger.error("Failed to connect to Postgres: %s", e)
        raise
 
 
def upsert(conn, table, columns, values, conflict_cols, id_column=None):
    """Generic INSERT ... ON CONFLICT DO UPDATE, returning the row id.
 
    Parameters
    ----------
    conn : psycopg2 connection
    table : str
    columns : list[str]
    values : tuple
    conflict_cols : list[str]   columns forming the unique constraint
    id_column : str, optional   primary key column; defaults to "{table}_id"
    """
    if id_column is None:
        id_column = f"{table}_id"

    col_list = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    conflict_list = ", ".join(conflict_cols)
 
    update_cols = [c for c in columns if c not in conflict_cols]
    if update_cols:
        update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)
        conflict_action = f"DO UPDATE SET {update_clause}"
    else:
        conflict_action = "DO NOTHING"
 
    query = f"""
        INSERT INTO {table} ({col_list})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_list}) {conflict_action}
        RETURNING {id_column};
    """
 
    with conn.cursor() as cur:
        cur.execute(query, values)
        row = cur.fetchone()
        conn.commit()
 
        if row is None:
            # DO NOTHING path with no update columns and a pre-existing row
            select_where = " AND ".join(f"{c} = %s" for c in conflict_cols)
            conflict_values = tuple(values[columns.index(c)] for c in conflict_cols)
            cur.execute(
                f"SELECT {id_column} FROM {table} WHERE {select_where};",
                conflict_values,
            )
            row = cur.fetchone()
 
        return row[0]
 
 
def upsert_city(conn, name, country, latitude, longitude):
    """Insert or return existing dim_city row. Conflict on (name, country)."""
    return upsert(
        conn,
        table="dim_city",
        columns=["name", "country", "latitude", "longitude"],
        values=(name, country, latitude, longitude),
        conflict_cols=["name", "country"],
        id_column="city_id",
    )
 
 
def insert_raw_weather(conn, city_id, http_status, payload):
    """Insert a raw API response into raw_weather. Returns raw_weather_id."""
    query = """
        INSERT INTO raw_weather (city_id, http_status, payload)
        VALUES (%s, %s, %s)
        RETURNING raw_weather_id;
    """
    with conn.cursor() as cur:
        cur.execute(query, (city_id, http_status, psycopg2.extras.Json(payload)))
        raw_weather_id = cur.fetchone()[0]
        conn.commit()
        return raw_weather_id
 
 
def upsert_fact_weather(conn, city_id, observed_at, temperature_c,
                        humidity_pct, wind_speed_kmh, wind_direction_deg,
                        precipitation_mm, condition, raw_weather_id):
    """Upsert into fact_weather. Conflict on (city_id, observed_at)."""
    return upsert(
        conn,
        table="fact_weather",
        columns=[
            "city_id", "observed_at", "temperature_c", "humidity_pct",
            "wind_speed_kmh", "wind_direction_deg", "precipitation_mm",
            "condition", "raw_weather_id",
        ],
        values=(
            city_id, observed_at, temperature_c, humidity_pct,
            wind_speed_kmh, wind_direction_deg, precipitation_mm,
            condition, raw_weather_id,
        ),
        conflict_cols=["city_id", "observed_at"],
        id_column="weather_id",
    )
 
 
def insert_alert(conn, weather_id, city_id, alert_type, severity, message,
                triggered_value, threshold_value):
    """Insert a weather_alert row (ON CONFLICT DO NOTHING)."""
    query = """
        INSERT INTO weather_alert (
            weather_id, city_id, alert_type, severity, message,
            triggered_value, threshold_value
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (weather_id, alert_type) DO NOTHING
        RETURNING alert_id;
    """
    with conn.cursor() as cur:
        cur.execute(query, (
            weather_id, city_id, alert_type, severity, message,
            triggered_value, threshold_value,
        ))
        row = cur.fetchone()
        conn.commit()
        if row:
            logger.info("Alert inserted: %s for city_id=%s", alert_type, city_id)
        else:
            logger.debug("Alert already exists: %s for weather_id=%s", alert_type, weather_id)
        return row[0] if row else None
 
 
def mark_raw_processed(conn, raw_weather_id):
    """Flag a raw_weather row as processed=TRUE, processed_at=now()."""
    query = """
        UPDATE raw_weather
        SET processed = TRUE, processed_at = now()
        WHERE raw_weather_id = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (raw_weather_id,))
        conn.commit()
 
