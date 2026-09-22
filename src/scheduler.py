"""
WeatherPulse scheduler.py — recurring pipeline runner (APScheduler).

Wires extract -> transform -> alerts on an interval, or runs once.

Usage:
    python -m src.scheduler --run-once          # single run
    python -m src.scheduler                      # every 60 min (default)
    python -m src.scheduler --interval-minutes 30

NOTE: This is a stub skeleton. Implementation TODOs are marked inline.
"""

# TODO: import argparse, logging
# TODO: from apscheduler.schedulers.blocking import BlockingScheduler
# TODO: from . import extract, transform, alerts


def job():
    """Run the full pipeline: extract -> transform -> alerts."""
    # TODO: extract.run()
    # TODO: transform.run()
    # TODO: alerts.run()
    raise NotImplementedError


def main():
    """Parse CLI args and either run once or start the blocking scheduler."""
    # TODO: argparse: --run-once, --interval-minutes (default 60)
    # TODO: if run_once: job(); return
    # TODO: scheduler = BlockingScheduler()
    # TODO: scheduler.add_job(job, "interval", minutes=..., id="weatherpulse_pipeline")
    # TODO: scheduler.start()
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: logging.basicConfig(...)
    main()