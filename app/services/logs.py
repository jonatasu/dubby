from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..config import settings


def log_event(message: str) -> None:
    try:
        logs_dir = settings.outputs_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).isoformat()
        line = f"[{ts}] {message}\n"
        (logs_dir / "events.log").open("a", encoding="utf-8").write(line)
    except Exception:
        # Logging nunca deve quebrar o fluxo principal
        pass
