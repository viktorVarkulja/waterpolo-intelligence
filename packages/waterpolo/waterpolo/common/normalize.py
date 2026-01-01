from __future__ import annotations

import re
from typing import Optional


def normalize_team_name(name: str) -> str:
    return " ".join(name.strip().split())


def slugify(name: str) -> str:
    slug = name.lower().replace("/", " ").replace("-", " ")
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug


def normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", label.lower())


def parse_int(value: str | int | None) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = value.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None
