from __future__ import annotations

from pathlib import Path
import subprocess
import shutil
from typing import Optional


def run_ffmpeg(args: list[str]) -> None:
    cmd = ["ffmpeg", "-y", *args]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            "ffmpeg não encontrado no PATH. Instale o ffmpeg no host ou use o container Docker."
        ) from e


def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def extract_audio(input_media: Path, out_wav: Path, sr: int = 16000) -> Path:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(["-i", str(input_media), "-vn", "-ac", "1", "-ar", str(sr), "-acodec", "pcm_s16le", str(out_wav)])
    return out_wav


def mux_video_with_audio(input_media: Path, input_audio: Path, output_media: Path) -> Path:
    output_media.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(["-i", str(input_media), "-i", str(input_audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-shortest", str(output_media)])
    return output_media
