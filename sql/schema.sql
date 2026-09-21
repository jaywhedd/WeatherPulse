-- WeatherPulse Schema
-- Run: psql -U postgres -d weatherpulse -f sql/schema.sql

-- City reference data
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    country     TEXT NOT NULL,
    latitude    NUMERIC(9,6) NOT NULL,
    longitude   NUMERIC(9,6) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(name, country)
);

-- Raw API responses
CREATE TABLE IF NOT EXISTS raw_weather (
    raw_weather_id BIGSERIAL PRIMARY KEY,
    city_id        INTEGER NOT NULL REFERENCES dim_city(city_id),
    fetched_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    http_status    INTEGER,
    payload        JSONB NOT NULL,
    processed      BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_raw_weather_processed ON raw_weather(processed, raw_weather_id);
CREATE INDEX IF NOT EXISTS idx_raw_weather_city ON raw_weather(city_id);

-- Normalized observations
CREATE TABLE IF NOT EXISTS fact_weather (
    weather_id         BIGSERIAL PRIMARY KEY,
    city_id            INTEGER NOT NULL REFERENCES dim_city(city_id),
    observed_at        TIMESTAMPTZ NOT NULL,
    temperature_c      NUMERIC(5,2),
    humidity_pct       NUMERIC(5,2),
    wind_speed_kmh     NUMERIC(6,2),
    wind_direction_deg NUMERIC(6,2),
    precipitation_mm   NUMERIC(6,2),
    condition          TEXT,
    raw_weather_id     BIGINT NOT NULL REFERENCES raw_weather(raw_weather_id),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(city_id, observed_at)
);
CREATE INDEX IF NOT EXISTS idx_fact_city_ts ON fact_weather(city_id, observed_at);

-- Threshold-triggered alerts
CREATE TABLE IF NOT EXISTS weather_alert (
    alert_id         BIGSERIAL PRIMARY KEY,
    weather_id       BIGINT NOT NULL REFERENCES fact_weather(weather_id),
    city_id          INTEGER NOT NULL REFERENCES dim_city(city_id),
    alert_type       TEXT NOT NULL,
    severity         TEXT NOT NULL DEFAULT 'HIGH',
    message          TEXT,
    triggered_value  NUMERIC(8,2),
    threshold_value  NUMERIC(8,2),
    triggered_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(weather_id, alert_type)
);