from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import MatchDetail, MatchOut, MatchPlayerLine, MatchTeamStats
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


@router.get("/{match_id}", response_model=MatchDetail)
def get_match(match_id: int, session: Session = Depends(get_session)) -> MatchDetail:
    match = crud.get_match(session, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    team_stats = crud.list_match_team_stats(session, match.id)
    team_stats_payload = []
    for stat in team_stats:
        stats = {
            "goals": stat.to_g,
            "shots": stat.to_sh,
            "shooting_pct": float(stat.to_g) / float(stat.to_sh) if stat.to_sh else 0.0,
            "extra_man_goals": stat.ex_g,
            "extra_man_shots": stat.ex_sh,
            "extra_man_pct": float(stat.ex_g) / float(stat.ex_sh) if stat.ex_sh else 0.0,
            "center_goals": stat.ce_g,
            "center_shots": stat.ce_sh,
            "counter_goals": stat.co_g,
            "counter_shots": stat.co_sh,
            "assists": stat.assists,
            "turnovers": stat.turnovers,
            "steals": stat.steals,
            "blocks": stat.blocks,
            "sprints_won": stat.sprints_won,
            "sprints": stat.sprints,
            "exclusions_drawn": stat.exclusions_drawn,
            "exclusions_fouls": stat.exclusions_fouls,
        }
        team_stats_payload.append(
            MatchTeamStats(
                team_id=stat.team_id,
                team_name=_team_name(session, stat.team_id),
                is_home=stat.team_id == match.home_team_id,
                stats=stats,
            )
        )

    player_rows = crud.list_match_player_stats(session, match.id)
    player_stats_payload = [
        MatchPlayerLine(
            player_id=player.id,
            player_name=player.name,
            team_id=team.id if team else None,
            team_name=team.name if team else None,
            goals=stats.goals,
            shots=stats.shots,
            assists=stats.assists,
            steals=stats.steals,
            blocks=stats.blocks,
            exclusions=stats.exclusions,
            turnovers=stats.turnovers,
        )
        for stats, player, team in player_rows
    ]

    return MatchDetail(
        id=match.id,
        season=match.season,
        stage=match.stage,
        date=match.date,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_team=_team_name(session, match.home_team_id),
        away_team=_team_name(session, match.away_team_id),
        home_score=match.home_score,
        away_score=match.away_score,
        venue=None,
        team_stats=team_stats_payload,
        player_stats=player_stats_payload,
    )
