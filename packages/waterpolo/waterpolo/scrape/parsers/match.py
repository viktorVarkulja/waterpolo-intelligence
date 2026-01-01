from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Dict, List, Tuple

from waterpolo.common.normalize import parse_int
from waterpolo.scrape.models import Match, Player, PlayerMatchStats, TeamMatchStats
from waterpolo.scrape.parsers.stats import map_player_stats, map_stats


def _season_from_filename(filename: str | None) -> str | None:
    if not filename:
        return None
    match = re.search(r"(CL\d{2})", filename)
    return match.group(1) if match else None


def _parse_microplus_stats(headers: List[str], values: List[str]) -> Dict[str, int]:
    stats: Dict[str, int] = {}
    header_map = {h.lower().strip(): h for h in headers}
    for raw_header, value in zip(headers, values):
        header = raw_header.lower().strip()
        if header == "%":
            continue
        if "/" in value:
            left, right = value.split("/", 1)
            made = parse_int(left) or 0
            att = parse_int(right) or 0
            if header == "total":
                stats["ToG"] = made
                stats["ToSh"] = att
            elif header == "a":
                stats["AG"] = made
                stats["ASh"] = att
            elif header == "c":
                stats["CeG"] = made
                stats["CeSh"] = att
            elif header == "x":
                stats["EXG"] = made
                stats["EXSh"] = att
            elif header == "6m":
                stats["6mG"] = made
                stats["6mSh"] = att
            elif header == "ps":
                stats["PG"] = made
                stats["PSh"] = att
            elif header == "ca":
                stats["CoG"] = made
                stats["CoSh"] = att
            elif header.startswith("pso"):
                stats["PSOG"] = made
                stats["PSOSh"] = att
            elif header.startswith("sp"):
                stats["SpW"] = made
                stats["Sp"] = att
        else:
            value_int = parse_int(value) or 0
            if header == "as":
                stats["As"] = value_int
            elif header == "tf":
                stats["To"] = value_int
            elif header == "st":
                stats["St"] = value_int
            elif header.startswith("bl"):
                stats["Bl"] = value_int
            elif header == "sp":
                stats["Sp"] = value_int
            elif header.startswith("sp"):
                stats["SpW"] = value_int
            elif header == "18c":
                stats["ExCe"] = value_int
            elif header == "18f":
                stats["ExF"] = value_int
            elif header == "2ex":
                stats["DoEx"] = value_int
            elif header == "p":
                stats["P"] = value_int
            elif header == "ex":
                stats["ExFin"] = value_int
            elif header.startswith("4ex"):
                stats["Ex4min"] = value_int
    return stats


def _parse_microplus_match(payload: Dict[str, Any]) -> Tuple[Match, List[TeamMatchStats], List[Player], List[PlayerMatchStats]]:
    filename = payload.get("jsonfilename")
    match_id = filename.split("/")[-1].replace(".JSON", "") if filename else ""
    season = _season_from_filename(match_id)
    match_date = None
    if payload.get("dd"):
        try:
            match_date = datetime.strptime(payload.get("dd"), "%d/%m/%Y").date()
        except ValueError:
            match_date = None

    match = Match(
        match_id=match_id,
        season=season,
        stage=payload.get("d_en"),
        date=match_date,
        time_utc=payload.get("h"),
        venue=payload.get("v"),
        home_team=payload.get("d1_en"),
        away_team=payload.get("d2_en"),
        home_score=payload.get("r1"),
        away_score=payload.get("r2"),
        source_url=None,
        scraped_at=datetime.utcnow(),
    )

    headers = payload.get("s_en", [])
    team_stats = [
        TeamMatchStats(match_id=match_id, team_name=payload.get("d1_en"), stats=_parse_microplus_stats(headers, payload.get("s1_t", []))),
        TeamMatchStats(match_id=match_id, team_name=payload.get("d2_en"), stats=_parse_microplus_stats(headers, payload.get("s2_t", []))),
    ]

    players: List[Player] = []
    player_stats: List[PlayerMatchStats] = []
    for player in payload.get("s1_s", []) + payload.get("s2_s", []):
        team_name = match.home_team if player.get("teamCod") == payload.get("s1") else match.away_team
        player_id = player.get("cg") or player.get("c")
        player_model = Player(
            player_id=str(player_id),
            team_name=team_name,
            name=player.get("cognNome") or f"{player.get('n', '')} {player.get('c', '')}".strip(),
            number=parse_int(player.get("nn")),
            position=player.get("r_en"),
            dob=None,
            source_url=None,
        )
        players.append(player_model)
        stats = map_player_stats(headers, player.get("s", []))
        if "TOTAL" in headers:
            total_idx = headers.index("TOTAL")
            total_val = player.get("s", [])[total_idx] if player.get("s") else ""
            if total_val and "/" in total_val:
                made, att = total_val.split("/", 1)
                stats["goals"] = parse_int(made)
                stats["shots"] = parse_int(att)
        player_stats.append(
            PlayerMatchStats(
                match_id=match_id,
                player_id=str(player_id),
                stats=stats,
            )
        )

    return match, team_stats, players, player_stats


def parse_match(payload: Dict[str, Any]) -> Tuple[Match, List[TeamMatchStats], List[Player], List[PlayerMatchStats]]:
    if payload.get("Document", {}).get("Cod") == "STA":
        return _parse_microplus_match(payload)
    match_info = payload.get("match", {})
    match = Match(
        match_id=str(match_info.get("match_id")),
        season=match_info.get("season"),
        stage=match_info.get("stage"),
        date=match_info.get("date"),
        time_utc=match_info.get("time_utc"),
        venue=match_info.get("venue"),
        home_team=match_info.get("home_team"),
        away_team=match_info.get("away_team"),
        home_score=match_info.get("home_score"),
        away_score=match_info.get("away_score"),
        source_url=match_info.get("source_url"),
        scraped_at=datetime.utcnow(),
    )

    stats: List[TeamMatchStats] = []
    for team_block in payload.get("team_stats", []):
        headers = team_block.get("headers", [])
        values = team_block.get("values", [])
        stats.append(
            TeamMatchStats(
                match_id=match.match_id,
                team_name=team_block.get("team_name"),
                stats=map_stats(headers, values),
            )
        )

    return match, stats, [], []
