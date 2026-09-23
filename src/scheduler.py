"""
WeatherPulse scheduler.py — recurring pipeline runner (APScheduler).

Wires extract -> transform -> alerts on an interval, or runs once.

Usage:
    python -m src.scheduler --run-once          # single run
    python -m src.scheduler                      # every 60 min (default)
    python -m src.scheduler --interval-minutes 30
"""

import argparse
import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from . import extract, transform, alerts

logger = logging.getLogger(__name__)


def job():
    """Run the full pipeline: extract -> transform -> alerts."""
    logger.info("Pipeline run starting")

    logger.info("Stage: extract")
    extract.run()

    logger.info("Stage: transform")
    transform.run()

    logger.info("Stage: alerts")
    alerts.run()

    logger.info("Pipeline run complete")


def main():
    """Parse CLI args and either run once or start the blocking scheduler."""
    parser = argparse.ArgumentParser(description="WeatherPulse pipeline scheduler")
    parser.add_argument("--run-once", action="store_true", help="Run the pipeline once and exit")
    parser.add_argument("--interval-minutes", type=int, default=60, help="Interval between runs (default: 60)")
    args = parser.parse_args()

    if args.run_once:
        job()
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(job, "interval", minutes=args.interval_minutes, id="weatherpulse_pipeline")

    logger.info("Scheduler started — running every %d minute(s). Ctrl+C to stop.", args.interval_minutes)

    # Run once immediately on startup, then let the interval take over
    job()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()