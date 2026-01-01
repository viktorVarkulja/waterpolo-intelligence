from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import TeamCompare, TeamOut

router = APIRouter()


@router.get("/compare", response_model=TeamCompare)
def compare_teams(
    teamA: int = Query(..., alias="teamA"),
    teamB: int = Query(..., alias="teamB"),
    season: str | None = Query(None),
    stage: str | None = Query(None),
    window: int | None = Query(None),
    session: Session = Depends(get_session),
) -> TeamCompare:
    team_a = crud.get_team(session, teamA)
    team_b = crud.get_team(session, teamB)
    if not team_a or not team_b:
        raise HTTPException(status_code=404, detail="Team not found")

    agg_a = crud.team_aggregates(session, team_a.id)
    agg_b = crud.team_aggregates(session, team_b.id)

    deltas = {k: float(agg_a[k]) - float(agg_b[k]) for k in agg_a}
    return TeamCompare(
        team_a=TeamOut(id=team_a.id, name=team_a.name, slug=team_a.slug, aggregates=agg_a),
        team_b=TeamOut(id=team_b.id, name=team_b.name, slug=team_b.slug, aggregates=agg_b),
        deltas=deltas,
    )
