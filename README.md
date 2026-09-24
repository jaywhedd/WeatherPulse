# WeatherPulse

ETL pipeline for weather data ingestion, transformation, and threshold alerting with PostgreSQL + Python.

WeatherPulse extracts current observations for a list of cities from the [Open-Meteo API](https://open-meteo.com/), preserves the raw JSON responses, transforms them into normalized PostgreSQL tables, and raises alerts when observations cross configured thresholds. It can run once on demand or on a recurring schedule.

## Repo Structure
```
WeatherPulse/
├── src/
│   ├── extract.py       # calls Open-Meteo API, writes to raw_weather
│   ├── transform.py     # raw_weather -> fact_weather (parses JSONB)
│   ├── load.py          # db connection + upsert logic
│   ├── alerts.py        # threshold checks -> weather_alert
│   └── scheduler.py     # APScheduler entrypoint (or cron wrapper)
├── sql/
│   └── schema.sql       # dim_city, raw_weather, fact_weather, weather_alert
├── config/
│   └── cities.yaml      # cities + lat/long to track, alert thresholds
├── notebooks/
│   └── analysis.ipynb   # summary stats for demo
├── requirements.txt
├── .env                 # POSTGRES_* credentials (uncommitted)
└── README.md
```

## Prerequisites

- Python 3.11+
- PostgreSQL 16 (any local install works; this repo also runs with the bundled `.pg/` binaries see [Local PostgreSQL](#local-postgresql))
- A virtual environment in `.venv/`

## Setup

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install ipykernel   # only needed to run the notebook
```

### 2. Configure the database connection

Create a `.env` file in the project root (it is git-ignored):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=weatherpulse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

> Note: the pipeline reads plain `POSTGRES_*` environment variables,there is no dotenv loader in the code, so either export these in your shell before running, or use the `cmd /c set ...` style shown below.

### 3. Create the database and load the schema

```bash
psql -U postgres -c "CREATE DATABASE weatherpulse;"
psql -U postgres -d weatherpulse -f sql/schema.sql
```

## Usage

### Run the pipeline once

```bash
cmd /c "set POSTGRES_HOST=localhost&& set POSTGRES_PORT=5432&& set POSTGRES_DB=weatherpulse&& set POSTGRES_USER=postgres&& set POSTGRES_PASSWORD=&& .venv\Scripts\python.exe -m src.scheduler --run-once"
```

Each run does three stages:
1. **Extract** - fetch current weather per configured city, store raw JSON in `raw_weather`.
2. **Transform** - parse unprocessed raw records into clean rows in `fact_weather`.
3. **Alerts** - compare observations against thresholds, insert rows into `weather_alert`.

### Run on a schedule

```bash
.venv\Scripts\python.exe -m src.scheduler                    # every 60 minutes (default)
.venv\Scripts\python.exe -m src.scheduler --interval-minutes 30
```

Press `Ctrl+C` to stop.

### Open the analysis notebook

Open `notebooks/analysis.ipynb` in VS Code (or Jupyter), select the `.venv` Python kernel, and run the cells. It reports:

- Row counts per table (`dim_city`, `raw_weather`, `fact_weather`, `weather_alert`)
- Alerts grouped by city and type
- The most recent fetch time

> Tip: one run gives you one observation per city. To build up trend data for a demo, either let the scheduler run for a while or run `--run-once` a few times.

### Configure cities and thresholds

Edit `config/cities.yaml`. Cities need a `latitude`/`longitude` because Open-Meteo resolves by coordinates, not name. Alert thresholds live in the same file under `alerts:` (max/min temperature, wind speed, precipitation).

### Inspect the database

```sql
-- connect with: psql -U postgres -d weatherpulse
SELECT count(*) FROM dim_city;
SELECT count(*) FROM raw_weather;
SELECT count(*) FROM fact_weather;
SELECT count(*) FROM weather_alert;

-- daily average temperature by city
SELECT c.name, DATE(f.observed_at) AS observation_date,
       AVG(f.temperature_c) AS average_temperature
FROM fact_weather f
JOIN dim_city c ON c.city_id = f.city_id
GROUP BY c.name, DATE(f.observed_at)
ORDER BY observation_date;
```

## Local PostgreSQL

This machine has PostgreSQL 16 installed as portable binaries in `.pg/` (not a system service ,not listed in `Program Files`, and `psql` is not on `PATH`). Use the bundled executables instead:

```bash
# start the server (trust auth, user "postgres", no password)
.pg\bin\pg_ctl.exe -D .pg\data -l .pg\logfile start

# check status / stop
.pg\bin\pg_ctl.exe -D .pg\data status
.pg\bin\pg_ctl.exe -D .pg\data stop

# these binaries do NOT ship psql/createdb — run one-off SQL via Python:
.venv\Scripts\python.exe -c "import psycopg2; c=psycopg2.connect(dbname='weatherpulse',user='postgres'); cur=c.cursor(); cur.execute('SELECT count(*) FROM fact_weather'); print(cur.fetchone()[0], 'rows'); c.close()"
```

The cluster already contains the `weatherpulse` database with the schema loaded.

#### WeThinkCode_ verification
WTC-3G57YLHT