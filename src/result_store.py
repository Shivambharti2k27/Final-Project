"""Small helper for merging reproducible run metrics into one JSON file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "results" / "metrics.json"


def update_metrics(section: str, values: dict[str, Any]) -> None:
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}
    metrics[section] = values
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")