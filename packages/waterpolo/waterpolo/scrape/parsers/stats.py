from __future__ import annotations

from typing import Dict, List

from waterpolo.common.normalize import normalize_label, parse_int

LABEL_MAP = {
    "tog": "ToG",
    "tosh": "ToSh",
    "ag": "AG",
    "ash": "ASh",
    "ceg": "CeG",
    "cesh": "CeSh",
    "exg": "EXG",
    "exsh": "EXSh",
    "6mg": "6mG",
    "6msh": "6mSh",
    "pg": "PG",
    "psh": "PSh",
    "cog": "CoG",
    "cosh": "CoSh",
    "psog": "PSOG",
    "psosh": "PSOSh",
    "assists": "As",
    "turnovers": "To",
    "steals": "St",
    "blocks": "Bl",
    "sprintswon": "SpW",
    "sprints": "Sp",
    "spw": "SpW",
    "sp": "Sp",
    "exclusionsdrawn": "ExCe",
    "exclusionsfouls": "ExF",
    "doubleexclusions": "DoEx",
    "penalties": "P",
    "exclusionsfinished": "ExFin",
    "exclusions4min": "Ex4min",
}

PLAYER_LABEL_MAP = {
    "g": "goals",
    "goals": "goals",
    "s": "shots",
    "shots": "shots",
    "a": "assists",
    "assists": "assists",
    "st": "steals",
    "steals": "steals",
    "bl": "blocks",
    "blocks": "blocks",
    "ex": "exclusions",
    "exclusions": "exclusions",
    "to": "turnovers",
    "turnovers": "turnovers",
}


def map_stats(headers: List[str], values: List[str]) -> Dict[str, int]:
    stats: Dict[str, int] = {}
    for header, value in zip(headers, values):
        key = LABEL_MAP.get(normalize_label(header))
        if not key:
            continue
        parsed = parse_int(value)
        stats[key] = parsed if parsed is not None else 0
    return stats


def map_player_stats(headers: List[str], values: List[str]) -> Dict[str, int | None]:
    stats: Dict[str, int | None] = {}
    for header, value in zip(headers, values):
        key = PLAYER_LABEL_MAP.get(normalize_label(header))
        if not key:
            continue
        stats[key] = parse_int(value)
    return stats
