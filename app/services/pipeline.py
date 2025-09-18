from __future__ import annotations

from pathlib import Path
import time
import logging

from .media import extract_audio, mux_video_with_audio, has_ffmpeg
from .asr import transcribe
from .translate import translate_text
from .tts import synthesize_segments_with_clone, save_wav
from ..config import settings

logger = logging.getLogger(__name__)


async def process_media(input_media: Path, src_lang: str, dst_lang: str, audio_only: bool | None = None) -> Path:
    t0 = time.perf_counter()
    logger.info({"event": "pipeline_start", "input": str(input_media), "src": src_lang, "dst": dst_lang})

    # 1) Extração
    phase_start = time.perf_counter()
    wav_path = input_media.with_suffix(".16k.wav")
    extract_audio(input_media, wav_path, sr=16000)
    logger.info({"event": "phase_end", "phase": "extract_audio", "seconds": round(time.perf_counter() - phase_start, 3)})

    # 2) ASR
    phase_start = time.perf_counter()
    segments = transcribe(wav_path, language=None if src_lang == "auto" else src_lang)
    logger.info({"event": "phase_end", "phase": "asr", "segments": len(segments), "seconds": round(time.perf_counter() - phase_start, 3)})
    for i, seg in enumerate(segments[:3]):
        logger.debug({"event": "asr_sample", "idx": i, "start": seg.start, "end": seg.end, "text": seg.text[:120]})

    # 3) Tradução
    phase_start = time.perf_counter()
    translated_segments: list[tuple[float, float, str]] = []
    for seg in segments:
        source_language = src_lang if src_lang != "auto" else "en"
        text = translate_text(seg.text, source_language, dst_lang)
        translated_segments.append((seg.start, seg.end, text))
        if len(translated_segments) <= 3:
            logger.debug({"event": "translate_sample", "src": seg.text[:80], "dst": text[:80]})
    logger.info({"event": "phase_end", "phase": "translate", "segments": len(translated_segments), "seconds": round(time.perf_counter() - phase_start, 3)})

    # 4) TTS / Clonagem
    phase_start = time.perf_counter()
    logger.info({"event": "phase_start", "phase": "tts_clone"})
    audio = synthesize_segments_with_clone(translated_segments, wav_path, target_language=dst_lang, sr=16000)
    dubbed_wav = settings.outputs_dir / f"{input_media.stem}.dubbed.wav"
    save_wav(dubbed_wav, audio, sr=16000)
    logger.info({"event": "phase_end", "phase": "tts_clone", "seconds": round(time.perf_counter() - phase_start, 3), "duration_s": round(len(audio)/16000, 2)})

    # 5) Mux
    phase_start = time.perf_counter()
    if audio_only is True or (audio_only is None and not has_ffmpeg()):
        output_path = dubbed_wav
        mux_used = False
    else:
        output_path = settings.outputs_dir / f"{input_media.stem}.dubbed.mp4"
        try:
            mux_video_with_audio(input_media, dubbed_wav, output_path)
            mux_used = True
        except Exception as e:
            logger.warning({"event": "mux_failed", "error": str(e)})
            output_path = dubbed_wav
            mux_used = False
    logger.info({"event": "phase_end", "phase": "mux", "mux_used": mux_used, "seconds": round(time.perf_counter() - phase_start, 3)})

    total = round(time.perf_counter() - t0, 3)
    logger.info({"event": "pipeline_complete", "output": str(output_path), "total_seconds": total})
    return output_path
