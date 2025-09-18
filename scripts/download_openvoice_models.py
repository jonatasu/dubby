#!/usr/bin/env python3
"""Download OpenVoice pretrained models.

This script fetches the required OpenVoice checkpoints for multilingual voice cloning.
It stores them under models/openvoice/ preserving expected directory structure.

If a corporate proxy/SSL blocks downloads, instruct the user how to place models manually.
"""
from __future__ import annotations

import sys
import shutil
from pathlib import Path
import urllib.request
from typing import TypedDict, List, Optional

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models" / "openvoice"

class ModelFile(TypedDict):
    name: str
    url: str
    sha256: Optional[str]

# Minimal model set (can be expanded)
# NOTE: URLs assume public availability; adjust if OpenVoice publishes different asset layout.
MODEL_FILES: List[ModelFile] = [
    {
        "name": "gpt_encoder.pt",
        "url": "https://huggingface.co/myshell-ai/OpenVoice/resolve/main/gpt_encoder.pt?download=1",
        "sha256": None,
    },
    {
        "name": "tone_color_converter.pt",
        "url": "https://huggingface.co/myshell-ai/OpenVoice/resolve/main/tone_color_converter.pt?download=1",
        "sha256": None,
    },
]


def safe_download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"Downloading {url} -> {dest}")
        with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def main():
    print("== Download OpenVoice Models ==")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    success = True
    for mf in MODEL_FILES:
        target: Path = MODELS_DIR / mf["name"]
        if target.exists() and target.stat().st_size > 0:
            print(f"✔ Already present: {target.name}")
            continue
        if not safe_download(mf["url"], target):
            success = False

    if not success:
        print("Some files failed to download. If you are behind corporate SSL/proxy:")
        print("1. Manually download the files listed above.")
        print(f"2. Place them inside: {MODELS_DIR}")
        print("3. Re-run the application.")
        sys.exit(1)

    print("All OpenVoice model files downloaded.")


if __name__ == "__main__":
    main()
