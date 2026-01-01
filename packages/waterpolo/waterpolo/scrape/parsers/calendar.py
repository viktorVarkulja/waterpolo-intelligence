from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from waterpolo.scrape.models import Match


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_microplus_date(date_str: str, time_str: str | None) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        base = datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None
    if time_str:
        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            parsed_time = time(0, 0)
    else:
        parsed_time = time(0, 0)
    return datetime.combine(base, parsed_time)


def _parse_microplus(payload: Dict[str, Any]) -> List[Match]:
    matches: List[Match] = []
    season = payload.get("cp")
    for entry in payload.get("e", []):
        match_path = None
        if entry.get("c0") and entry.get("c1") and entry.get("c2") and entry.get("c3") and entry.get("c4") and entry.get("c5"):
            # MicroPlus match folders follow c4 (home) then c5 (away) ordering, e.g. ASM1A011MLAOLY
            match_path = f"{entry.get('c0')}{entry.get('c1')}{entry.get('c2')}{entry.get('c3')}{entry.get('c4')}{entry.get('c5')}"
        match_id = match_path or str(entry.get("nm") or "")
        dt = _parse_microplus_date(entry.get("gi"), entry.get("h"))
        matches.append(
            Match(
                match_id=f"{season}-{match_id}" if season and match_id else match_id,
                season=season,
                stage=entry.get("d_en") or entry.get("d_it"),
                date=dt.date() if dt else None,
                time_utc=entry.get("h"),
                venue=entry.get("v"),
                home_team=entry.get("dt1"),
                away_team=entry.get("dt2"),
                home_score=int(entry.get("s1_p")) if entry.get("s1_p") else None,
                away_score=int(entry.get("s2_p")) if entry.get("s2_p") else None,
                source_url=entry.get("url") or None,
                scraped_at=datetime.utcnow(),
            )
        )
    return matches


def parse_calendar(payload: Dict[str, Any]) -> List[Match]:
    if "e" in payload:
        return _parse_microplus(payload)
    matches: List[Match] = []
    for item in payload.get("matches", []):
        dt = _parse_date(item.get("date"))
        match = Match(
            match_id=str(item.get("match_id")),
            season=item.get("season"),
            stage=item.get("stage"),
            date=dt.date() if dt else None,
            time_utc=dt.time().isoformat() if dt else None,
            venue=item.get("venue"),
            home_team=item.get("home_team"),
            away_team=item.get("away_team"),
            home_score=item.get("home_score"),
            away_score=item.get("away_score"),
            source_url=item.get("source_url"),
            scraped_at=datetime.utcnow(),
        )
        matches.append(match)
    return matches
