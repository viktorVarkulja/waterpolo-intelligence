from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Health(BaseModel):
    status: str


class MetaFreshness(BaseModel):
    last_import: Optional[datetime]
    team_count: int
    match_count: int
    team_match_stat_count: int


class TeamBase(BaseModel):
    id: int
    name: str
    slug: str


class TeamAggregate(BaseModel):
    matches: int
    goals_per_match: float
    shooting_pct: float
    extra_man_pct: float
    center_pct: float
    counter_pct: float
    penalty_pct: float
    sprints_win_pct: float
    turnovers_per_match: float
    steals_per_match: float


class TeamOut(TeamBase):
    aggregates: TeamAggregate


class TeamDetail(TeamBase):
    aggregates: TeamAggregate


class TeamTrendPoint(BaseModel):
    match_index: int
    goals: int
    shots: int
    shooting_pct: float


class TeamTrends(BaseModel):
    team_id: int
    window: int
    points: List[TeamTrendPoint]

class TeamMatchOut(BaseModel):
    match_id: int
    date: Optional[date]
    stage: Optional[str]
    opponent: str
    home: bool
    team_score: Optional[int]
    opponent_score: Optional[int]


class TeamCompare(BaseModel):
    team_a: TeamOut
    team_b: TeamOut
    deltas: Dict[str, float]


class PlayerOut(BaseModel):
    id: int
    team_id: Optional[int]
    name: str
    number: Optional[int]
    position: Optional[str]


class PlayerDetail(PlayerOut):
    dob: Optional[date]
    source_url: Optional[str]

class PlayerTrendPoint(BaseModel):
    match_index: int
    goals: Optional[int]
    shots: Optional[int]
    assists: Optional[int]


class PlayerTrends(BaseModel):
    player_id: int
    window: int
    points: List[PlayerTrendPoint]


class PlayerMatchOut(BaseModel):
    match_id: int
    date: Optional[date]
    opponent: str
    home: bool
    goals: Optional[int]
    shots: Optional[int]
    assists: Optional[int]
    steals: Optional[int]
    blocks: Optional[int]
    exclusions: Optional[int]
    turnovers: Optional[int]

class MatchOut(BaseModel):
    id: int
    season: Optional[str]
    stage: Optional[str]
    date: Optional[date]
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    venue: Optional[str] = None


class CsvImportRequest(BaseModel):
    path: Optional[str] = None


class ImportResult(BaseModel):
    rows_inserted: int


class ScrapeResult(BaseModel):
    status: str


class ScrapeRequest(BaseModel):
    season: str
    stage: Optional[str] = None
    calendar_url: Optional[str] = None


class CalendarFile(BaseModel):
    file: str
    date: Optional[str] = None
    counter: str


class OptionsResponse(BaseModel):
    schedules: list[CalendarFile]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
