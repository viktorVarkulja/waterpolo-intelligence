from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from waterpolo.common.constants import TEAM_STAT_DB_MAP
from waterpolo.common.normalize import normalize_team_name, slugify
from waterpolo.common.team_aliases import TEAM_ALIASES
from waterpolo.db import upsert_team_match_stats
from waterpolo.db_models import Match, Player, PlayerMatchStats, Team, TeamMatchStats
from waterpolo.etl.cleaning import clean_team_stats
from waterpolo.etl.loaders import load_csv
from waterpolo.scrape.discovery import discover_endpoints
from waterpolo.scrape.models import Match as MatchModel
from waterpolo.scrape.models import Player as PlayerModel
from waterpolo.scrape.models import PlayerMatchStats as PlayerMatchStatsModel
from waterpolo.scrape.models import TeamMatchStats as TeamMatchStatsModel
from waterpolo.scrape.sources.euro_aquatics import EuroAquaticsSource
from waterpolo.scrape.sources.microplus import MicroPlusSource
from waterpolo.common.logging import get_logger

DEFAULT_ENDPOINTS_PATH = Path("config/endpoints.json")
logger = get_logger("scrape.storage")


def _canonical_team_name(name: str) -> str:
    norm = normalize_team_name(name)
    for canonical, aliases in TEAM_ALIASES.items():
        if norm.lower() == canonical.lower():
            return canonical
        if any(norm.lower() == alias.lower() for alias in aliases):
            return canonical
    return norm


def _match_id_fallback(match: MatchModel) -> str:
    raw = "|".join(
        [
            match.season or "",
            match.stage or "",
            str(match.date) if match.date else "",
            match.home_team,
            match.away_team,
            match.venue or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _player_id_fallback(player: PlayerModel, season: Optional[str]) -> str:
    raw = "|".join(
        [
            season or "",
            player.team_name,
            player.name,
            str(player.number) if player.number is not None else "",
            str(player.dob) if player.dob else "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _get_or_create_team(session: Session, name: str) -> Team:
    canonical = _canonical_team_name(name)
    team = session.execute(select(Team).where(Team.name == canonical)).scalar_one_or_none()
    if team:
        return team
    team = Team(name=canonical, slug=slugify(canonical))
    session.add(team)
    session.flush()
    return team


def upsert_match(session: Session, match: MatchModel) -> Match:
    match_id = match.match_id or _match_id_fallback(match)
    db_match = session.execute(select(Match).where(Match.match_key == match_id)).scalar_one_or_none()
    if db_match:
        if match.season:
            db_match.season = match.season
        db_match.stage = match.stage
        db_match.date = match.date
        db_match.home_score = match.home_score
        db_match.away_score = match.away_score
        db_match.source_url = match.source_url
        return db_match

    home_team = _get_or_create_team(session, match.home_team)
    away_team = _get_or_create_team(session, match.away_team)

    db_match = Match(
        season=match.season,
        stage=match.stage,
        date=match.date,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        home_score=match.home_score,
        away_score=match.away_score,
        source_url=match.source_url,
        match_key=match_id,
        import_batch=datetime.utcnow().strftime("scrape-%Y%m%d"),
    )
    session.add(db_match)
    try:
        session.flush()
        return db_match
    except IntegrityError:
        session.rollback()
        logger.warning("Match key conflict, loading existing match_key=%s", match_id)
        existing = session.execute(select(Match).where(Match.match_key == match_id)).scalar_one()
        return existing


def upsert_team_stats(session: Session, match: Match, stats: Iterable[TeamMatchStatsModel]) -> int:
    inserted = 0
    for entry in stats:
        team = _get_or_create_team(session, entry.team_name)
        db_stats = session.get(TeamMatchStats, {"match_id": match.id, "team_id": team.id})
        if not db_stats:
            db_stats = TeamMatchStats(match_id=match.id, team_id=team.id)
            session.add(db_stats)

        for src, dest in TEAM_STAT_DB_MAP.items():
            setattr(db_stats, dest, int(entry.stats.get(src, 0)))

        inserted += 1
    return inserted


def upsert_players(session: Session, players: Iterable[PlayerModel], season: Optional[str]) -> int:
    inserted = 0
    for player in players:
        player_id = player.player_id or _player_id_fallback(player, season)
        db_player = session.execute(select(Player).where(Player.source_url == player_id)).scalar_one_or_none()
        team = _get_or_create_team(session, player.team_name)
        if not db_player:
            db_player = Player(
                team_id=team.id,
                name=player.name,
                number=player.number,
                position=player.position,
                dob=player.dob,
                source_url=player_id,
            )
            session.add(db_player)
            inserted += 1
        else:
            db_player.team_id = team.id
    return inserted


def upsert_player_stats(session: Session, stats: Iterable[PlayerMatchStatsModel]) -> int:
    inserted = 0
    for entry in stats:
        db_player = session.execute(select(Player).where(Player.source_url == entry.player_id)).scalar_one_or_none()
        db_match = session.execute(select(Match).where(Match.match_key == entry.match_id)).scalar_one_or_none()
        if not db_player or not db_match:
            continue
        db_stats = PlayerMatchStats(
            match_id=db_match.id,
            player_id=db_player.id,
            goals=entry.stats.get("goals"),
            shots=entry.stats.get("shots"),
            assists=entry.stats.get("assists"),
            steals=entry.stats.get("steals"),
            blocks=entry.stats.get("blocks"),
            exclusions=entry.stats.get("exclusions"),
            turnovers=entry.stats.get("turnovers"),
        )
        session.add(db_stats)
        inserted += 1
    return inserted


def load_endpoints(path: Path = DEFAULT_ENDPOINTS_PATH) -> Dict[str, str]:
    env_path = os.getenv("WATERPOLO_ENDPOINTS_PATH")
    if env_path:
        path = Path(env_path)
    if path.exists():
        logger.info("Loading endpoints from %s", path)
        return json.loads(path.read_text(encoding="utf-8"))
    logger.warning("Endpoints file missing at %s, generating placeholder", path)
    return discover_endpoints(path)


def _has_endpoints(endpoints: Dict[str, str]) -> bool:
    return any(value for value in endpoints.values())


def _calendar_base_from_endpoints(endpoints: Dict[str, str]) -> str:
    calendar_url = endpoints.get("calendar", "")
    if "export/PNChampionsLeague/" in calendar_url:
        return calendar_url.split("export/PNChampionsLeague/")[0] + "export/PNChampionsLeague/"
    return calendar_url.rsplit("/", 1)[0] + "/"


def _build_calendar_url(base: str, file_path: str) -> str:
    if file_path.startswith("http"):
        return file_path
    if base.endswith("export/PNChampionsLeague/") and file_path.startswith("export/PNChampionsLeague/"):
        return base + file_path.split("export/PNChampionsLeague/")[-1]
    return base + file_path.lstrip("/")


def seed_from_csv(session: Session, path: str) -> Dict[str, int]:
    df = clean_team_stats(load_csv(path))
    rows = upsert_team_match_stats(session, df)
    return {"rows_inserted": rows}


def run_scrape_full(
    session: Session,
    season: str,
    stage: Optional[str] = None,
    calendar_url: Optional[str] = None,
) -> Dict[str, int]:
    endpoints = load_endpoints()
    source = MicroPlusSource(endpoints) if _has_endpoints(endpoints) else EuroAquaticsSource(endpoints)
    logger.info("Starting scrape_full season=%s stage=%s", season, stage)
    if stage == "all":
        contatori = list_contatori()
        schedules = contatori.get("schedules", [])
        calendar_base = _calendar_base_from_endpoints(endpoints)
        matches = []
        for item in schedules:
            url = _build_calendar_url(calendar_base, item["file"])
            logger.info("Fetching calendar file=%s", url)
            matches.extend(source.fetch_calendar_file(url))
    elif calendar_url:
        matches = source.fetch_calendar_file(calendar_url)
    else:
        matches = source.fetch_calendar(season=season, stage=stage)

    match_count = 0
    stat_count = 0
    seen_match_ids = set()
    for match in matches:
        if match.match_id in seen_match_ids:
            logger.info("Skipping duplicate match_id=%s", match.match_id)
            continue
        if match.home_score is None and match.away_score is None:
            logger.info("Skipping unplayed match_id=%s", match.match_id)
            continue
        seen_match_ids.add(match.match_id)
        logger.info("Processing match %s vs %s", match.home_team, match.away_team)
        db_match = upsert_match(session, match)
        match_count += 1
        match_model, team_stats, players, player_stats = source.fetch_match(match.match_id)
        if not match_model.season:
            match_model.season = match.season or season
        db_match = upsert_match(session, match_model)
        stat_count += upsert_team_stats(session, db_match, team_stats)
        upsert_players(session, players, match_model.season)
        upsert_player_stats(session, player_stats)

    logger.info("Scrape complete matches=%s team_stats=%s", match_count, stat_count)
    return {"matches": match_count, "team_stats": stat_count}


def run_scrape_match(session: Session, match_id: str) -> Dict[str, int]:
    endpoints = load_endpoints()
    source = MicroPlusSource(endpoints) if _has_endpoints(endpoints) else EuroAquaticsSource(endpoints)
    logger.info("Starting scrape_match match_id=%s", match_id)
    match_model, team_stats, players, player_stats = source.fetch_match(match_id)
    db_match = upsert_match(session, match_model)
    stat_count = upsert_team_stats(session, db_match, team_stats)
    upsert_players(session, players, match_model.season)
    upsert_player_stats(session, player_stats)
    logger.info("Scrape match complete match_id=%s team_stats=%s", match_id, stat_count)
    return {"matches": 1, "team_stats": stat_count}


def run_scrape_rosters(session: Session, season: str) -> Dict[str, int]:
    endpoints = load_endpoints()
    source = MicroPlusSource(endpoints) if _has_endpoints(endpoints) else EuroAquaticsSource(endpoints)
    logger.info("Starting scrape_rosters season=%s", season)
    players = source.fetch_rosters(season=season)
    player_count = upsert_players(session, players, season)
    logger.info("Scrape rosters complete players=%s", player_count)
    return {"players": player_count}


def list_contatori() -> Dict[str, List[Dict[str, str]]]:
    endpoints = load_endpoints()
    source = MicroPlusSource(endpoints)
    return source.fetch_contatori()
