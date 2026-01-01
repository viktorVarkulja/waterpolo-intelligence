from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from waterpolo.common.logging import get_logger


@dataclass
class ClientConfig:
    base_url: Optional[str] = None
    timeout: int = 20
    rate_limit_per_sec: float = 1.0
    user_agent: str = "waterpolo-scraper/0.1"


class HttpClient:
    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self._last_request_ts = 0.0
        self.logger = get_logger(self.__class__.__name__)

        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"User-Agent": self.config.user_agent})

    def _sleep_for_rate_limit(self) -> None:
        if self.config.rate_limit_per_sec <= 0:
            return
        delay = 1.0 / self.config.rate_limit_per_sec
        elapsed = time.time() - self._last_request_ts
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        self._sleep_for_rate_limit()
        url = f"{self.config.base_url}{path}" if self.config.base_url else path
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        self._last_request_ts = time.time()
        response.raise_for_status()
        return response

    def get_json(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        response = self.get(path, params=params)
        return response.json()

    def save_snapshot(self, payload: Any, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
