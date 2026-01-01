from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import PlayerDetail, PlayerMatchOut, PlayerOut, PlayerTrends
from waterpolo.db_models import Team

router = APIRouter(prefix="/players")


@router.get("", response_model=list[PlayerOut])
def list_players(
    season: str | None = Query(None),
    stage: str | None = Query(None),
    team: int | None = Query(None),
    role: str | None = Query(None),
    q: str | None = Query(None),
    session: Session = Depends(get_session),
) -> list[PlayerOut]:
    players = crud.list_players_filtered(session, team_id=team, role=role, query=q)
    stats_map = crud.player_aggregates(session, [player.id for player in players], season=season, stage=stage)
    return [
        PlayerOut(
            id=player.id,
            team_id=player.team_id,
            name=player.name,
            number=player.number,
            position=player.position,
            team_name=player.team.name if player.team else None,
            stats=stats_map.get(player.id),
        )
        for player in players
    ]


@router.get("/{player_id}", response_model=PlayerDetail)
def get_player(player_id: int, session: Session = Depends(get_session)) -> PlayerDetail:
    player = crud.get_player(session, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    stats_map = crud.player_aggregates(session, [player.id])
    return PlayerDetail(
        id=player.id,
        team_id=player.team_id,
        name=player.name,
        number=player.number,
        position=player.position,
        dob=player.dob,
        source_url=player.source_url,
        team_name=player.team.name if player.team else None,
        stats=stats_map.get(player.id),
    )


@router.get("/{player_id}/trends", response_model=PlayerTrends)
def get_player_trends(
    player_id: int,
    window: int = Query(5, ge=1, le=20),
    season: str | None = Query(None),
    stage: str | None = Query(None),
    session: Session = Depends(get_session),
) -> PlayerTrends:
    matches = crud.list_player_matches(session, player_id, season=season, stage=stage)
    points = []
    for idx, (_, stats) in enumerate(matches):
        points.append(
            {
                "match_index": idx + 1,
                "goals": stats.goals,
                "shots": stats.shots,
                "assists": stats.assists,
            }
        )
    return PlayerTrends(player_id=player_id, window=window, points=points)


@router.get("/{player_id}/matches", response_model=list[PlayerMatchOut])
def get_player_matches(
    player_id: int,
    season: str | None = Query(None),
    stage: str | None = Query(None),
    session: Session = Depends(get_session),
) -> list[PlayerMatchOut]:
    player = crud.get_player(session, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    matches = crud.list_player_matches(session, player_id, season=season, stage=stage)
    results: list[PlayerMatchOut] = []
    for match, stats in matches:
        home = match.home_team_id == player.team_id
        opponent_id = match.away_team_id if home else match.home_team_id
        opponent = session.get(Team, opponent_id)
        results.append(
            PlayerMatchOut(
                match_id=match.id,
                date=match.date,
                opponent=opponent.name if opponent else "Unknown",
                home=home,
                goals=stats.goals,
                shots=stats.shots,
                assists=stats.assists,
                steals=stats.steals,
                blocks=stats.blocks,
                exclusions=stats.exclusions,
                turnovers=stats.turnovers,
            )
        )
    return results
