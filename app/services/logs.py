from __future__ import annotations
import json
import logging
import time
from typing import Any, Dict
from datetime import datetime, timezone
from ..config import settings

_LOG = logging.getLogger("dubby.events")

def log_event(event: str, **fields: Any) -> None:
    """Emit structured JSON log (stdout)."""
    record: Dict[str, Any] = {"event": event, "ts": time.time()}
    record.update(fields)
    try:
        _LOG.info(json.dumps(record, ensure_ascii=False))
    except Exception:
        _LOG.info({"event": event, **fields})

def append_event_line(message: str) -> None:
    """Append plain text line to outputs/logs/events.log (best-effort)."""
    try:
        logs_dir = settings.outputs_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        line = f"[{ts}] {message}\n"
        with (logs_dir / "events.log").open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass
