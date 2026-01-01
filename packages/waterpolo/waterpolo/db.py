from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from waterpolo.common.constants import TEAM_STAT_COLUMNS, TEAM_STAT_DB_MAP
from waterpolo.db_models import Match, Team, TeamMatchStats


def _slugify(name: str) -> str:
    return name.lower().replace("/", " ").replace("-", " ").strip().replace(" ", "-")


def _match_key(home: str, away: str, home_score: int | None, away_score: int | None, idx: int) -> str:
    raw = f"{home}|{away}|{home_score}|{away_score}|{idx}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _get_or_create_team(session: Session, name: str) -> Team:
    team = session.execute(select(Team).where(Team.name == name)).scalar_one_or_none()
    if team:
        return team
    team = Team(name=name, slug=_slugify(name))
    session.add(team)
    session.flush()
    return team


def upsert_team_match_stats(session: Session, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    rows_inserted = 0
    df = df.reset_index(drop=True)
    for idx in range(0, len(df), 2):
        if idx + 1 >= len(df):
            break
        home_row = df.iloc[idx]
        away_row = df.iloc[idx + 1]

        home_name = str(home_row["Teams"])
        away_name = str(away_row["Teams"])
        home_team = _get_or_create_team(session, home_name)
        away_team = _get_or_create_team(session, away_name)

        home_score = int(home_row.get("ToG", 0))
        away_score = int(away_row.get("ToG", 0))
        match_key = _match_key(home_name, away_name, home_score, away_score, idx)

        match = session.execute(select(Match).where(Match.match_key == match_key)).scalar_one_or_none()
        if not match:
            match = Match(
                season=None,
                stage=None,
                date=None,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_score=home_score,
                away_score=away_score,
                source_url=None,
                match_key=match_key,
                import_batch=datetime.utcnow().strftime("csv-%Y%m%d"),
            )
            session.add(match)
            session.flush()

        for team, row in ((home_team, home_row), (away_team, away_row)):
            stats = session.get(TeamMatchStats, {"match_id": match.id, "team_id": team.id})
            if not stats:
                stats = TeamMatchStats(match_id=match.id, team_id=team.id)
                session.add(stats)

            for src, dest in TEAM_STAT_DB_MAP.items():
                value = int(row.get(src, 0)) if src in row else 0
                setattr(stats, dest, value)

            rows_inserted += 1

    return rows_inserted
