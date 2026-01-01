from __future__ import annotations

from typing import Any, Dict, List

from waterpolo.common.normalize import parse_int
from waterpolo.scrape.models import Player


def parse_roster(payload: Dict[str, Any]) -> List[Player]:
    if "n" in payload:
        return _parse_microplus_rosters(payload)
    players: List[Player] = []
    for item in payload.get("players", []):
        players.append(
            Player(
                player_id=str(item.get("player_id")),
                team_name=item.get("team_name"),
                name=item.get("name"),
                number=item.get("number"),
                position=item.get("position"),
                dob=item.get("dob"),
                source_url=item.get("source_url"),
            )
        )
    return players


def _parse_microplus_rosters(payload: Dict[str, Any]) -> List[Player]:
    players: List[Player] = []
    for team_block in payload.get("n", []):
        team_name = team_block.get("d_en") or team_block.get("sq_nc") or team_block.get("c")
        for player in team_block.get("p", []):
            players.append(
                Player(
                    player_id=str(player.get("cod")),
                    team_name=team_name,
                    name=player.get("cognNome") or f"{player.get('no', '')} {player.get('co', '')}".strip(),
                    number=parse_int(player.get("num")),
                    position=player.get("r_en"),
                    dob=None,
                    source_url=None,
                )
            )
    return players
