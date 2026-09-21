# WeatherPulse — Project Wiki

## Home

### WeatherPulse — Weather ETL Pipeline

A solo data engineering project that builds an end-to-end ETL pipeline for weather data using Python and PostgreSQL.

WeatherPulse extracts observations from the Open-Meteo API, preserves raw responses as JSON, transforms them into normalized relational data, and detects severe weather using configurable thresholds.

### Goals

- Extract weather data for configured cities.
- Preserve raw API responses for traceability.
- Transform JSON into normalized PostgreSQL tables.
- Detect severe weather with threshold-based alerts.
- Schedule recurring pipeline runs.
- Support backfill, trend analysis, and demonstrations.

### Pipeline Overview

```text
Open-Meteo API -> Extract -> raw_weather -> Transform -> fact_weather
                                                        |
                                                        +-> Analysis
                                                        +-> Alert checks -> weather_alert
```

### Technology Stack

- Python
- PostgreSQL
- Open-Meteo API
- `psycopg2`, `requests`, `APScheduler`, `PyYAML`, `pandas`, `matplotlib`

## Wiki Pages

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Database Schema](#database-schema)
- [Build Steps](#build-steps)
- [Commands](#commands)
- [Tools and Setup](#tools-and-setup)
- [Configuration](#configuration)
- [Alerting](#alerting)
- [Backfill and Analysis](#backfill-and-analysis)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Scope and Stretch Goals](#scope-and-stretch-goals)
- [Diary Log](#diary-log)
- [Planning](#planning)

## Project Overview

WeatherPulse demonstrates a complete weather workflow from API extraction through database storage, transformation, alerting, scheduling, and analysis.

### Core Deliverable

The repository should fetch weather data, store raw responses, transform observations, load them safely, detect severe conditions, run on a schedule, backfill historical data, and demonstrate analytical queries in a video.

### Scope

Version one uses one weather source and a small configured city list. It does not include multi-source integration, streaming infrastructure, a web dashboard, machine-learning forecasting, or cloud deployment.

## Architecture

```text
config/cities.yaml
        |
        v
   scheduler.py
        |
        +--> extract.py --> Open-Meteo API --> raw_weather
        +--> transform.py ------------------> fact_weather
        +--> alerts.py ---------------------> weather_alert
```

| Component | Responsibility |
|---|---|
| `extract.py` | Calls the API and stores raw JSON payloads. |
| `transform.py` | Parses raw JSONB and creates structured observations. |
| `load.py` | Manages PostgreSQL connections, transactions, and upserts. |
| `alerts.py` | Compares observations against thresholds. |
| `scheduler.py` | Runs the pipeline on a recurring schedule. |
| `schema.sql` | Defines PostgreSQL tables and constraints. |
| `cities.yaml` | Defines tracked cities and configuration. |
| `analysis.ipynb` | Demonstrates queries and charts. |

## Data Pipeline

### Extract

For every configured city, the pipeline sends a request to Open-Meteo, records the fetch time and response status, and stores the unmodified response in `raw_weather`.

### Transform

The transform stage reads unprocessed raw records and extracts temperature, humidity, wind, precipitation, condition, and observation timestamps into `fact_weather`.

### Load

Database writes use transactions and upserts. A city and observation timestamp should identify one logical observation, preventing duplicates during retries or backfills.

### Alert

New fact rows are evaluated against configured thresholds. Matches are written to `weather_alert` with type, severity, values, and timestamps.

## Database Schema

### `dim_city`

City reference data: `city_id`, name, country, latitude, longitude, and creation timestamp.

### `raw_weather`

Raw ingestion data: `raw_weather_id`, `city_id`, fetch timestamp, HTTP status, JSONB payload, and processing timestamp.

### `fact_weather`

Clean observations: `weather_id`, `city_id`, observed timestamp, temperature, humidity, wind speed, wind direction, precipitation, condition, and source raw record.

### `weather_alert`

Threshold matches: `alert_id`, `weather_id`, `city_id`, alert type, severity, message, triggered value, threshold value, and timestamp.

## Build Steps

1. Create the PostgreSQL database.
2. Configure environment variables.
3. Add cities to `config/cities.yaml`.
4. Apply `sql/schema.sql`.
5. Implement and test extraction.
6. Implement transformation and validation.
7. Add PostgreSQL loading and upserts.
8. Implement threshold checks.
9. Add one-time and scheduled execution.
10. Add backfill, analysis, tests, and the demo video.

## Commands

```bash
python -m venv .venv
.venv\\Scripts\\activate             # Windows
source .venv/bin/activate              # macOS/Linux
pip install -r weather-etl-pipeline/requirements.txt
psql -U postgres -d weatherpulse -f weather-etl-pipeline/sql/schema.sql
python weather-etl-pipeline/src/extract.py
python weather-etl-pipeline/src/transform.py
python weather-etl-pipeline/src/alerts.py
python weather-etl-pipeline/src/scheduler.py --run-once
python weather-etl-pipeline/src/scheduler.py
jupyter notebook weather-etl-pipeline/notebooks/analysis.ipynb
```

## Tools and Setup

- Python 3.10+
- PostgreSQL 14+
- Git, pip, and Jupyter Notebook

Example `.env` configuration:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=weatherpulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

Keep `.env` uncommitted.

## Configuration

`config/cities.yaml` should contain the name, country, latitude, and longitude of each tracked city. It may also contain scheduler settings and alert thresholds.

```yaml
alerts:
  temperature_max_c: 40
  temperature_min_c: -10
  wind_speed_max_kmh: 60
  precipitation_max_mm: 25
```

## Alerting

Suggested alert types:

- `EXTREME_HEAT`
- `EXTREME_COLD`
- `HIGH_WIND`
- `HEAVY_PRECIPITATION`

The demonstration should show at least one record in `weather_alert`. A lower temporary demonstration threshold may be used if documented.

## Backfill and Analysis

Backfill creates enough observations to demonstrate trends, city comparisons, and alert behavior. The notebook should include row counts, sample records, average temperature by city, daily temperature trends, precipitation totals, alert summaries, and charts.

```sql
SELECT c.name, DATE(f.observed_at) AS observation_date,
       AVG(f.temperature_c) AS average_temperature
FROM fact_weather f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.name, DATE(f.observed_at)
ORDER BY observation_date;
```

## Testing

> **Status note (trimmed `requirements.txt`):** Formal pytest suites are deferred until after the demo — `pytest`/`pytest-cov` were removed from the dependencies. The immediate priority is the manual end-to-end check (final demo checklist below`. Once the pipeline works, re-add `pytest` and add pure-logic tests (threshold eval, JSON transformation` if time allows.



### Unit Tests

- City configuration parsing
- API response parsing
- JSON transformation
- Weather condition mapping
- Threshold evaluation
- Alert creation logic

### Integration Tests

- PostgreSQL connectivity
- Raw record insertion
- Fact table upserts
- Alert insertion
- End-to-end pipeline execution

Validate API status codes, required JSON fields, coordinates, timestamps, null measurements, duplicates, and transaction failures.

## Troubleshooting

### API Failures

Use timeouts, log failed requests, retry temporary failures, and allow the remaining cities to continue when one request fails.

### Database Errors

Confirm PostgreSQL is running, credentials are correct, the database exists, and the configured port is available.

### Duplicate Rows

Use a unique constraint on city and observation timestamp with an upsert strategy.

### No Alerts

Review threshold values, confirm `fact_weather` contains matching measurements, and verify the alert stage ran.

## Scope and Stretch Goals

### Version One

- One public weather API
- PostgreSQL storage
- Configurable cities
- Raw and structured layers
- Threshold alerts
- Scheduled execution
- Backfill and notebook analysis

### Future Enhancements

- Add a second weather API.
- Send alerts by email or Discord.
- Add Docker Compose and CI.
- Add data-quality checks and retry backoff.
- Deploy to the cloud.
- Add Airflow orchestration, a query API, or dashboard.

## Diary Log

Use this section as a running project journal.

### Entry Template

**Date:** `YYYY-MM-DD`

**Completed:**
- 

**Problems encountered:**
- 

**Decisions made:**
- 

**Next steps:**
- 

## Planning

### Initial Plan

1. Define scope and success criteria.
2. Select Open-Meteo as the initial source.
3. Design the PostgreSQL schema.
4. Create the repository structure.
5. Add configuration and environment handling.
6. Build extraction, transformation, loading, and alerting.
7. Add scheduling and backfill.
8. Create analysis queries and charts.
9. Test the complete pipeline.
10. Record the final demonstration.

### Final Demonstration Checklist

- Show the configured city list.
- Show the database schema.
- Run the pipeline.
- Show records in `raw_weather` and `fact_weather`.
- Show at least one `weather_alert` record.
- Run analytical queries.
- Display notebook charts.
- Demonstrate one-time or scheduled execution.

