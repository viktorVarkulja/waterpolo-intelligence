from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


def _parse_schedule_date(filename: str) -> str | None:
    # expects SCH_DDMMYYYY.JSON
    if "SCH_" not in filename:
        return None
    token = filename.split("SCH_")[-1].split(".")[0]
    try:
        dt = datetime.strptime(token, "%d%m%Y")
        return dt.date().isoformat()
    except ValueError:
        return None


def parse_contatori(payload: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    schedules: List[Dict[str, str]] = []
    rosters: List[Dict[str, str]] = []
    for entry in payload.get("contatori", []):
        cod = entry.get("cod")
        name = entry.get("nomefile") or ""
        if cod == "SCH_D":
            schedules.append(
                {
                    "file": name,
                    "date": _parse_schedule_date(name),
                    "counter": entry.get("counter") or "",
                }
            )
        elif cod == "TMR":
            rosters.append({"file": name, "counter": entry.get("counter") or ""})
    return {"schedules": schedules, "rosters": rosters}
