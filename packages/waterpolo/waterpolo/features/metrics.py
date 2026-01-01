from __future__ import annotations

from typing import Dict

import pandas as pd


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def derive_team_metrics(team_id: int, matches_df: pd.DataFrame) -> Dict[str, float]:
    team_matches = matches_df[matches_df["team_id"] == team_id]
    if team_matches.empty:
        return {}

    totals = team_matches.sum(numeric_only=True)
    metrics = {
        "matches": float(len(team_matches)),
        "goals_per_match": _safe_div(totals.get("to_g", 0), len(team_matches)),
        "shooting_pct": _safe_div(totals.get("to_g", 0), totals.get("to_sh", 0)),
        "extra_man_pct": _safe_div(totals.get("ex_g", 0), totals.get("ex_sh", 0)),
        "center_pct": _safe_div(totals.get("ce_g", 0), totals.get("ce_sh", 0)),
        "counter_pct": _safe_div(totals.get("co_g", 0), totals.get("co_sh", 0)),
        "penalty_pct": _safe_div(totals.get("p_g", 0), totals.get("p_sh", 0)),
        "sprints_win_pct": _safe_div(totals.get("sprints_won", 0), totals.get("sprints", 0)),
        "turnovers_per_match": _safe_div(totals.get("turnovers", 0), len(team_matches)),
        "steals_per_match": _safe_div(totals.get("steals", 0), len(team_matches)),
    }
    return metrics
