from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict

from .media import has_ffmpeg
from ..config import settings


def get_disk_usage(path: Path) -> dict[str, int]:
    try:
        st = shutil.disk_usage(path)
        return {"total": st.total, "used": st.used, "free": st.free}
    except Exception:
        return {"total": 0, "used": 0, "free": 0}


def current_asr_model() -> str:
    # Retorna caminho/config do modelo ASR atual
    return str(settings.asr_model)


def system_status() -> dict[str, Any]:
    return {
        "app": settings.app_name,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "ffmpeg": {
            "available": has_ffmpeg(),
        },
        "paths": {
            "uploads": str(settings.uploads_dir.resolve()),
            "outputs": str(settings.outputs_dir.resolve()),
            "models": str(settings.models_dir.resolve()),
        },
        "asr": {
            "model": current_asr_model(),
        },
        "disk": {
            "workspace": get_disk_usage(Path.cwd()),
            "outputs": get_disk_usage(settings.outputs_dir),
        },
    }
