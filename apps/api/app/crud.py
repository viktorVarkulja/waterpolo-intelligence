from __future__ import annotations

from typing import Dict, List, Tuple

from sqlalchemy import func, select, or_, and_
from sqlalchemy.orm import Session

from waterpolo.db_models import Match, Player, PlayerMatchStats, Team, TeamMatchStats


def get_meta_freshness(session: Session) -> Dict[str, int | None]:
    last_import = session.execute(select(func.max(Match.created_at))).scalar_one_or_none()
    team_count = session.execute(select(func.count(Team.id))).scalar_one()
    match_count = session.execute(select(func.count(Match.id))).scalar_one()
    stat_count = session.execute(select(func.count(TeamMatchStats.match_id))).scalar_one()
    return {
        "last_import": last_import,
        "team_count": team_count,
        "match_count": match_count,
        "team_match_stat_count": stat_count,
    }


def list_teams(session: Session) -> List[Team]:
    return session.execute(select(Team).order_by(Team.name)).scalars().all()


def get_team(session: Session, team_id: int) -> Team | None:
    return session.get(Team, team_id)


def get_team_by_slug(session: Session, slug: str) -> Team | None:
    return session.execute(select(Team).where(Team.slug == slug)).scalar_one_or_none()


def list_players(session: Session) -> List[Player]:
    return session.execute(select(Player).order_by(Player.name)).scalars().all()


def get_player(session: Session, player_id: int) -> Player | None:
    return session.get(Player, player_id)


def list_matches(session: Session, season: str | None = None, stage: str | None = None) -> List[Match]:
    stmt = select(Match)
    if season:
        stmt = stmt.where(Match.season == season)
    if stage and stage != "all":
        stmt = stmt.where(Match.stage == stage)
    return session.execute(stmt.order_by(Match.date.nulls_last())).scalars().all()


def get_match(session: Session, match_id: int) -> Match | None:
    return session.get(Match, match_id)


def list_team_matches(
    session: Session,
    team_id: int,
    season: str | None = None,
    stage: str | None = None,
) -> List[Match]:
    stmt = select(Match).where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
    if season:
        stmt = stmt.where(Match.season == season)
    if stage and stage != "all":
        stmt = stmt.where(Match.stage == stage)
    return session.execute(stmt.order_by(Match.date.nulls_last())).scalars().all()


def list_team_roster(session: Session, team_id: int) -> List[Player]:
    return session.execute(select(Player).where(Player.team_id == team_id).order_by(Player.name)).scalars().all()


def list_players_filtered(
    session: Session,
    team_id: int | None = None,
    role: str | None = None,
    query: str | None = None,
) -> List[Player]:
    stmt = select(Player)
    if team_id:
        stmt = stmt.where(Player.team_id == team_id)
    if role:
        stmt = stmt.where(Player.position == role)
    if query:
        stmt = stmt.where(Player.name.ilike(f"%{query}%"))
    return session.execute(stmt.order_by(Player.name)).scalars().all()


def list_player_matches(
    session: Session,
    player_id: int,
    season: str | None = None,
    stage: str | None = None,
) -> List[tuple[Match, PlayerMatchStats]]:
    stmt = (
        select(Match, PlayerMatchStats)
        .join(PlayerMatchStats, PlayerMatchStats.match_id == Match.id)
        .where(PlayerMatchStats.player_id == player_id)
    )
    if season:
        stmt = stmt.where(Match.season == season)
    if stage and stage != "all":
        stmt = stmt.where(Match.stage == stage)
    return session.execute(stmt.order_by(Match.date.nulls_last())).all()


def team_aggregates(session: Session, team_id: int) -> Dict[str, float]:
    stats = session.execute(
        select(TeamMatchStats).where(TeamMatchStats.team_id == team_id)
    ).scalars().all()

    if not stats:
        return {
            "matches": 0,
            "goals_per_match": 0.0,
            "shooting_pct": 0.0,
            "extra_man_pct": 0.0,
            "center_pct": 0.0,
            "counter_pct": 0.0,
            "penalty_pct": 0.0,
            "sprints_win_pct": 0.0,
            "turnovers_per_match": 0.0,
            "steals_per_match": 0.0,
        }

    def safe_div(n: int, d: int) -> float:
        return float(n) / float(d) if d else 0.0

    matches = len(stats)
    to_g = sum(s.to_g for s in stats)
    to_sh = sum(s.to_sh for s in stats)
    ex_g = sum(s.ex_g for s in stats)
    ex_sh = sum(s.ex_sh for s in stats)
    ce_g = sum(s.ce_g for s in stats)
    ce_sh = sum(s.ce_sh for s in stats)
    co_g = sum(s.co_g for s in stats)
    co_sh = sum(s.co_sh for s in stats)
    p_g = sum(s.p_g for s in stats)
    p_sh = sum(s.p_sh for s in stats)
    spw = sum(s.sprints_won for s in stats)
    sp = sum(s.sprints for s in stats)
    turnovers = sum(s.turnovers for s in stats)
    steals = sum(s.steals for s in stats)

    return {
        "matches": matches,
        "goals_per_match": safe_div(to_g, matches),
        "shooting_pct": safe_div(to_g, to_sh),
        "extra_man_pct": safe_div(ex_g, ex_sh),
        "center_pct": safe_div(ce_g, ce_sh),
        "counter_pct": safe_div(co_g, co_sh),
        "penalty_pct": safe_div(p_g, p_sh),
        "sprints_win_pct": safe_div(spw, sp),
        "turnovers_per_match": safe_div(turnovers, matches),
        "steals_per_match": safe_div(steals, matches),
    }


def team_trends(session: Session, team_id: int, window: int) -> List[Tuple[int, int, int, float]]:
    stats = session.execute(
        select(TeamMatchStats)
        .where(TeamMatchStats.team_id == team_id)
        .order_by(TeamMatchStats.match_id)
    ).scalars().all()

    points: List[Tuple[int, int, int, float]] = []
    for idx, stat in enumerate(stats):
        window_stats = stats[max(0, idx - window + 1) : idx + 1]
        goals = sum(s.to_g for s in window_stats)
        shots = sum(s.to_sh for s in window_stats)
        pct = float(goals) / float(shots) if shots else 0.0
        points.append((idx + 1, goals, shots, pct))

    return points
