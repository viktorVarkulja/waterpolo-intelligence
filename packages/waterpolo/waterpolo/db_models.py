from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    players = relationship("Player", back_populates="team")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    match_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    import_batch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TeamMatchStats(Base):
    __tablename__ = "team_match_stats"
    __table_args__ = (UniqueConstraint("match_id", "team_id", name="uq_team_match"),)

    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    to_g: Mapped[int] = mapped_column(Integer, default=0)
    to_sh: Mapped[int] = mapped_column(Integer, default=0)
    a_g: Mapped[int] = mapped_column(Integer, default=0)
    a_sh: Mapped[int] = mapped_column(Integer, default=0)
    ce_g: Mapped[int] = mapped_column(Integer, default=0)
    ce_sh: Mapped[int] = mapped_column(Integer, default=0)
    ex_g: Mapped[int] = mapped_column(Integer, default=0)
    ex_sh: Mapped[int] = mapped_column(Integer, default=0)
    six_m_g: Mapped[int] = mapped_column(Integer, default=0)
    six_m_sh: Mapped[int] = mapped_column(Integer, default=0)
    p_g: Mapped[int] = mapped_column(Integer, default=0)
    p_sh: Mapped[int] = mapped_column(Integer, default=0)
    co_g: Mapped[int] = mapped_column(Integer, default=0)
    co_sh: Mapped[int] = mapped_column(Integer, default=0)
    pso_g: Mapped[int] = mapped_column(Integer, default=0)
    pso_sh: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    turnovers: Mapped[int] = mapped_column(Integer, default=0)
    steals: Mapped[int] = mapped_column(Integer, default=0)
    blocks: Mapped[int] = mapped_column(Integer, default=0)
    sprints_won: Mapped[int] = mapped_column(Integer, default=0)
    sprints: Mapped[int] = mapped_column(Integer, default=0)
    exclusions_drawn: Mapped[int] = mapped_column(Integer, default=0)
    exclusions_fouls: Mapped[int] = mapped_column(Integer, default=0)
    double_exclusions: Mapped[int] = mapped_column(Integer, default=0)
    penalties: Mapped[int] = mapped_column(Integer, default=0)
    exclusions_finished: Mapped[int] = mapped_column(Integer, default=0)
    exclusions_4min: Mapped[int] = mapped_column(Integer, default=0)


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    team = relationship("Team", back_populates="players")


class PlayerMatchStats(Base):
    __tablename__ = "player_match_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    goals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shots: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    assists: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    steals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blocks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exclusions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    turnovers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
