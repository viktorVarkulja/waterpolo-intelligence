from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from waterpolo.common.logging import get_logger
from waterpolo.scrape.http_client import ClientConfig, HttpClient
from waterpolo.scrape.parsers.calendar import parse_calendar
from waterpolo.scrape.parsers.match import parse_match
from waterpolo.scrape.parsers.roster import parse_roster


class EuroAquaticsSource:
    def __init__(self, endpoints: Dict[str, str], base_url: str | None = None) -> None:
        self.endpoints = endpoints
        self.client = HttpClient(ClientConfig(base_url=base_url))
        self.logger = get_logger(self.__class__.__name__)

    def fetch_calendar(self, season: str, stage: str | None = None) -> List[Any]:
        endpoint = self.endpoints.get("calendar")
        if not endpoint:
            raise ValueError("Calendar endpoint not configured")
        payload = self.client.get_json(
            endpoint.format(season=season, stage=stage or ""),
            params=None,
        )
        return parse_calendar(payload)

    def fetch_match(self, match_id: str) -> Any:
        endpoint = self.endpoints.get("match")
        if not endpoint:
            raise ValueError("Match endpoint not configured")
        payload = self.client.get_json(endpoint.format(match_id=match_id))
        return parse_match(payload)

    def fetch_rosters(self, season: str) -> List[Any]:
        endpoint = self.endpoints.get("rosters")
        if not endpoint:
            raise ValueError("Rosters endpoint not configured")
        payload = self.client.get_json(endpoint.format(season=season))
        return parse_roster(payload)

    def snapshot(self, payload: Any, path: Path) -> None:
        self.client.save_snapshot(payload, path)
