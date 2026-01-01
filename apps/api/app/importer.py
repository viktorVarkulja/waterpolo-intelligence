from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from waterpolo import seed_from_csv


def import_csv(session: Session, path: str | None = None) -> int:
    csv_path = Path(path or settings.csv_default_path)
    result = seed_from_csv(session, str(csv_path))
    return result["rows_inserted"]
