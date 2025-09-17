from __future__ import annotations

from pathlib import Path
import numpy as np
import soundfile as sf

from ..config import settings


def synthesize_segment(text: str, sr: int = 16000, duration_per_char: float = 0.05) -> np.ndarray:
    # Fallback: gera um tom senoidal breve por caractere (placeholder)
    duration = max(0.3, min(5.0, len(text) * duration_per_char))
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    freq = 220.0
    audio = 0.1 * np.sin(2 * np.pi * freq * t).astype(np.float32)
    return audio


def synthesize_segments(segments: list[tuple[float, float, str]], sr: int = 16000) -> np.ndarray:
    # Concatena áudios por segmento, tentando aproximar o timing
    out = []
    for start, end, text in segments:
        seg_audio = synthesize_segment(text, sr=sr)
        target_len = int((end - start) * sr)
        if len(seg_audio) < target_len:
            pad = np.zeros(target_len - len(seg_audio), dtype=np.float32)
            seg_audio = np.concatenate([seg_audio, pad])
        else:
            seg_audio = seg_audio[:target_len]
        out.append(seg_audio)
    if out:
        return np.concatenate(out)
    return np.zeros(1, dtype=np.float32)


def save_wav(wav_path: Path, audio: np.ndarray, sr: int = 16000) -> Path:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(wav_path), audio, sr)
    return wav_path
