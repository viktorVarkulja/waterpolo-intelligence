from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import MatchOut
from waterpolo.db_models import Match, Team
from sqlalchemy import or_, and_

router = APIRouter(prefix="/matches")


def _team_name(session: Session, team_id: int) -> str:
    team = session.get(Team, team_id)
    return team.name if team else "Unknown"


@router.get("", response_model=list[MatchOut])
def list_matches(
    season: str | None = Query(None),
    stage: str | None = Query(None),
    team: int | None = Query(None),
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    close: bool | None = Query(None),
    session: Session = Depends(get_session),
) -> list[MatchOut]:
    matches = crud.list_matches(session, season=season, stage=stage)
    if team:
        matches = [m for m in matches if m.home_team_id == team or m.away_team_id == team]
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            matches = [m for m in matches if m.date and m.date >= from_dt]
        except ValueError:
            pass
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
            matches = [m for m in matches if m.date and m.date <= to_dt]
        except ValueError:
            pass
    if close:
        matches = [
            m
            for m in matches
            if m.home_score is not None and m.away_score is not None and abs(m.home_score - m.away_score) <= 2
        ]
    return [
        MatchOut(
            id=match.id,
            season=match.season,
            stage=match.stage,
            date=match.date,
            home_team=_team_name(session, match.home_team_id),
            away_team=_team_name(session, match.away_team_id),
            home_score=match.home_score,
            away_score=match.away_score,
            venue=None,
        )
        for match in matches
    ]


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: int, session: Session = Depends(get_session)) -> MatchOut:
    match = crud.get_match(session, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return MatchOut(
        id=match.id,
        season=match.season,
        stage=match.stage,
        date=match.date,
        home_team=_team_name(session, match.home_team_id),
        away_team=_team_name(session, match.away_team_id),
        home_score=match.home_score,
        away_score=match.away_score,
        venue=None,
    )
