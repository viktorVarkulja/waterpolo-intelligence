from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.importer import import_csv

scheduler = BackgroundScheduler(timezone="UTC")


def scheduled_import() -> None:
    session = SessionLocal()
    try:
        import_csv(session, None)
        session.commit()
    finally:
        session.close()


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(scheduled_import, "interval", hours=24, id="csv-import")
    scheduler.start()
