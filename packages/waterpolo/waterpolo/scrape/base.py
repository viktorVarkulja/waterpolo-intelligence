from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Protocol

import pandas as pd


class Scraper(Protocol):
    def fetch_team_match_stats(self) -> pd.DataFrame:
        ...

    def fetch_rosters(self) -> pd.DataFrame:
        ...

    def fetch_player_match_stats(self) -> pd.DataFrame:
        ...


class BaseScraper(ABC):
    @abstractmethod
    def fetch_team_match_stats(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def fetch_rosters(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def fetch_player_match_stats(self) -> pd.DataFrame:
        raise NotImplementedError
