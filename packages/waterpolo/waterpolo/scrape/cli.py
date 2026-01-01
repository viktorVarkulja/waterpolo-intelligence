from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from waterpolo.scrape.discovery import discover_endpoints
from waterpolo.scrape.storage import (
    run_scrape_full,
    run_scrape_match,
    run_scrape_rosters,
    seed_from_csv,
)

app = typer.Typer(help="Water Polo Champions League scraper")


def _session(database_url: str) -> Session:
    engine = create_engine(database_url)
    return Session(engine)


@app.command("scrape-discover")
def scrape_discover(out: Path = Path("config/endpoints.json")) -> None:
    discover_endpoints(out)
    typer.echo(f"Discovery config saved to {out}")


@app.command("scrape-calendar")
def scrape_calendar(
    season: str,
    stage: Optional[str] = None,
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo",
) -> None:
    with _session(database_url) as session:
        result = run_scrape_full(session, season=season, stage=stage)
        session.commit()
    typer.echo(result)


@app.command("scrape-match")
def scrape_match(
    match_id: str,
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo",
) -> None:
    with _session(database_url) as session:
        result = run_scrape_match(session, match_id=match_id)
        session.commit()
    typer.echo(result)


@app.command("scrape-rosters")
def scrape_rosters(
    season: str,
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo",
) -> None:
    with _session(database_url) as session:
        result = run_scrape_rosters(session, season=season)
        session.commit()
    typer.echo(result)


@app.command("scrape-full")
def scrape_full(
    season: str,
    stage: Optional[str] = None,
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo",
) -> None:
    with _session(database_url) as session:
        result = run_scrape_full(session, season=season, stage=stage)
        session.commit()
    typer.echo(result)


@app.command("ingest-csv")
def ingest_csv(
    path: Path,
    database_url: str = "postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo",
) -> None:
    with _session(database_url) as session:
        result = seed_from_csv(session, str(path))
        session.commit()
    typer.echo(result)
