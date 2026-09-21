# WeatherPulse
ETL pipeline for weather data ingestion, transformation, and threshold alerting with PostgreSQL + Python

## Repo Structure 
```
WeatherPulse/
├── src/
│   ├── extract.py       # calls Open-Meteo API, writes to raw_weather
│   ├── transform.py     # raw_weather -> fact_weather (parses JSONB)
│   ├── load.py          # db connection + upsert logic
│   ├── alerts.py         # threshold checks -> weather_alert
│   └── scheduler.py      # APScheduler entrypoint (or cron wrapper)
├── sql/
│   └── schema.sql        # tables above
├── config/
│   └── cities.yaml        # list of cities + lat/long to track
├── notebooks/
│   └── analysis.ipynb    # trend queries + charts for demo
├── requirements.txt
└── README.md
```


#### WeThinkCode_ verification 
WTC-3G57YLHT