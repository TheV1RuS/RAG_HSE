from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.utils import ensure_parent


def append_debug_record(path: str | Path, record: dict) -> None:
    out = ensure_parent(path)
    payload = dict(record)
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
