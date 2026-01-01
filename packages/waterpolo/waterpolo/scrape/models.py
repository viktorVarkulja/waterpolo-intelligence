from __future__ import annotations

from datetime import date as date_type, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Team(BaseModel):
    name: str
    slug: str
    aliases: List[str] = Field(default_factory=list)


class Match(BaseModel):
    match_id: str
    season: Optional[str] = None
    stage: Optional[str] = None
    date: Optional[date_type] = None
    time_utc: Optional[str] = None
    venue: Optional[str] = None
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    source_url: Optional[str] = None
    scraped_at: datetime


class TeamMatchStats(BaseModel):
    match_id: str
    team_name: str
    stats: Dict[str, int]


class Player(BaseModel):
    player_id: str
    team_name: str
    name: str
    number: Optional[int] = None
    position: Optional[str] = None
    dob: Optional[date_type] = None
    source_url: Optional[str] = None


class PlayerMatchStats(BaseModel):
    match_id: str
    player_id: str
    stats: Dict[str, Optional[int]]
