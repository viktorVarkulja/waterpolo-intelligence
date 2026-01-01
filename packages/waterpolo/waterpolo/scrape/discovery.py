from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from waterpolo.common.logging import get_logger


def discover_endpoints(output_path: Path) -> Dict[str, str]:
    logger = get_logger("discovery")
    logger.info("Discovery mode requires Selenium/Playwright instrumentation.")
    endpoints = {
        "calendar": "",
        "match": "",
        "rosters": "",
        "player_stats": "",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(endpoints, indent=2, ensure_ascii=True), encoding="utf-8")
    logger.info("Wrote placeholder endpoints to %s", output_path)
    return endpoints
