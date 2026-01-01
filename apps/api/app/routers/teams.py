from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import TeamDetail, TeamMatchOut, TeamOut, TeamTrends
from app.schemas import PlayerOut

router = APIRouter(prefix="/teams")


@router.get("", response_model=list[TeamOut])
def list_teams(
    season: str | None = Query(None),
    stage: str | None = Query(None),
    session: Session = Depends(get_session),
) -> list[TeamOut]:
    teams = crud.list_teams(session)
    results: list[TeamOut] = []
    for team in teams:
        aggregates = crud.team_aggregates(session, team.id)
        results.append(TeamOut(id=team.id, name=team.name, slug=team.slug, aggregates=aggregates))
    return results


@router.get("/{team_id}", response_model=TeamDetail)
def get_team(team_id: int, session: Session = Depends(get_session)) -> TeamDetail:
    team = crud.get_team(session, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    aggregates = crud.team_aggregates(session, team.id)
    return TeamDetail(id=team.id, name=team.name, slug=team.slug, aggregates=aggregates)


@router.get("/slug/{slug}", response_model=TeamDetail)
def get_team_by_slug(slug: str, session: Session = Depends(get_session)) -> TeamDetail:
    team = crud.get_team_by_slug(session, slug)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    aggregates = crud.team_aggregates(session, team.id)
    return TeamDetail(id=team.id, name=team.name, slug=team.slug, aggregates=aggregates)


@router.get("/{team_id}/trends", response_model=TeamTrends)
def get_team_trends(
    team_id: int,
    window: int = Query(5, ge=1, le=20),
    season: str | None = Query(None),
    stage: str | None = Query(None),
    session: Session = Depends(get_session),
) -> TeamTrends:
    points = crud.team_trends(session, team_id, window)
    return TeamTrends(
        team_id=team_id,
        window=window,
        points=[
            {"match_index": idx, "goals": goals, "shots": shots, "shooting_pct": pct}
            for idx, goals, shots, pct in points
        ],
    )


@router.get("/{team_id}/matches", response_model=list[TeamMatchOut])
def get_team_matches(
    team_id: int,
    season: str | None = Query(None),
    stage: str | None = Query(None),
    session: Session = Depends(get_session),
) -> list[TeamMatchOut]:
    matches = crud.list_team_matches(session, team_id, season=season, stage=stage)
    results: list[TeamMatchOut] = []
    for match in matches:
        home = match.home_team_id == team_id
        opponent_id = match.away_team_id if home else match.home_team_id
        opponent = crud.get_team(session, opponent_id)
        results.append(
            TeamMatchOut(
                match_id=match.id,
                date=match.date,
                stage=match.stage,
                opponent=opponent.name if opponent else "Unknown",
                home=home,
                team_score=match.home_score if home else match.away_score,
                opponent_score=match.away_score if home else match.home_score,
            )
        )
    return results


@router.get("/{team_id}/roster", response_model=list[PlayerOut])
def get_team_roster(
    team_id: int,
    season: str | None = Query(None),
    session: Session = Depends(get_session),
) -> list[PlayerOut]:
    players = crud.list_team_roster(session, team_id)
    return [
        PlayerOut(
            id=player.id,
            team_id=player.team_id,
            name=player.name,
            number=player.number,
            position=player.position,
        )
        for player in players
    ]
