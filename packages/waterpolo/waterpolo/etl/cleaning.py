from __future__ import annotations

from typing import Iterable

import pandas as pd

from waterpolo.common.constants import TEAM_STAT_COLUMNS


def normalize_team_name(name: str) -> str:
    return " ".join(name.strip().split())


def clean_team_stats(df: pd.DataFrame, required_columns: Iterable[str] | None = None) -> pd.DataFrame:
    required = set(required_columns or (["Teams"] + TEAM_STAT_COLUMNS))
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cleaned = df.copy()
    cleaned["Teams"] = cleaned["Teams"].astype(str).map(normalize_team_name)

    numeric_cols = [col for col in TEAM_STAT_COLUMNS if col in cleaned.columns]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int)

    cleaned = cleaned.drop_duplicates()
    return cleaned
