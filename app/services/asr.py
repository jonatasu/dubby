from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np
import soundfile as sf

from faster_whisper import WhisperModel
from huggingface_hub.errors import LocalEntryNotFoundError

from ..config import settings


_model: WhisperModel | None = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        try:
            _model = WhisperModel(
                settings.asr_model,
                compute_type=settings.asr_compute_type,  # auto on CPU/GPU
                download_root=str(settings.models_dir),
            )
        except LocalEntryNotFoundError as e:
            # Erro típico quando o tráfego de saída está bloqueado / SSL falha
            raise RuntimeError(
                "Modelo não encontrado no cache local e o download online está bloqueado. "
                "Baixe manualmente o modelo do Hugging Face e coloque em 'models/', "
                "ou ajuste o ambiente de rede/SSL. Dica: defina ASR_MODEL para um caminho local."
            ) from e
    return _model


@dataclass
class Segment:
    start: float
    end: float
    text: str


def load_audio(wav_path: Path) -> np.ndarray:
    audio, sr = sf.read(str(wav_path))
    if sr != 16000:
        raise ValueError("Expected 16kHz audio; ensure extract_audio used ar=16000")
    if audio.ndim > 1:
        audio = audio[:, 0]
    return audio.astype(np.float32)


def transcribe(wav_path: Path, language: str | None = None) -> List[Segment]:
    model = get_model()
    segments, _info = model.transcribe(str(wav_path), language=None if language in (None, "auto") else language)
    out: List[Segment] = []
    for s in segments:  # type: ignore[assignment]
        out.append(Segment(start=float(s.start), end=float(s.end), text=s.text.strip()))
    return out
