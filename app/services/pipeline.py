from __future__ import annotations

from pathlib import Path
import time
import logging
import uuid

from .media import extract_audio, mux_video_with_audio, has_ffmpeg
from .asr import transcribe
from .translate import translate_text
from .tts import synthesize_segments_with_clone, save_wav
from ..config import settings
from .logs import log_event

JOB_STATUS: dict[str, dict] = {}
METRICS = {"translate_fail": 0, "tts_fail": 0, "mux_fail": 0}

logger = logging.getLogger(__name__)


async def process_media(input_media: Path, src_lang: str, dst_lang: str, audio_only: bool | None = None, job_id: str | None = None) -> Path:
    t0 = time.perf_counter()
    job_id = job_id or uuid.uuid4().hex
    JOB_STATUS[job_id] = {"state": "running", "src": src_lang, "dst": dst_lang, "input": str(input_media), "started": time.time(), "phases": []}
    log_event("pipeline_start", job_id=job_id, input=str(input_media), src=src_lang, dst=dst_lang)

    # 1) Extração
    phase_start = time.perf_counter()
    wav_path = input_media.with_suffix(".16k.wav")
    extract_audio(input_media, wav_path, sr=16000)
    dur = round(time.perf_counter() - phase_start, 3)
    JOB_STATUS[job_id]["phases"].append({"phase": "extract_audio", "seconds": dur})
    log_event("phase_end", job_id=job_id, phase="extract_audio", seconds=dur)

    # 2) ASR
    phase_start = time.perf_counter()
    segments = transcribe(wav_path, language=None if src_lang == "auto" else src_lang)
    dur = round(time.perf_counter() - phase_start, 3)
    JOB_STATUS[job_id]["phases"].append({"phase": "asr", "seconds": dur, "segments": len(segments)})
    log_event("phase_end", job_id=job_id, phase="asr", segments=len(segments), seconds=dur)
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
            log_event("translate_sample", job_id=job_id, src_sample=seg.text[:80], dst_sample=text[:80])
    dur = round(time.perf_counter() - phase_start, 3)
    JOB_STATUS[job_id]["phases"].append({"phase": "translate", "seconds": dur, "segments": len(translated_segments)})
    log_event("phase_end", job_id=job_id, phase="translate", segments=len(translated_segments), seconds=dur)

    # 4) TTS / Clonagem
    phase_start = time.perf_counter()
    log_event("phase_start", job_id=job_id, phase="tts_clone")
    try:
        audio = synthesize_segments_with_clone(translated_segments, wav_path, target_language=dst_lang, sr=16000)
    except Exception as e:
        METRICS["tts_fail"] += 1
        JOB_STATUS[job_id]["error"] = f"tts_fail: {e}"
        raise
    dubbed_wav = settings.outputs_dir / f"{input_media.stem}.dubbed.wav"
    save_wav(dubbed_wav, audio, sr=16000)
    dur = round(time.perf_counter() - phase_start, 3)
    JOB_STATUS[job_id]["phases"].append({"phase": "tts_clone", "seconds": dur})
    log_event("phase_end", job_id=job_id, phase="tts_clone", seconds=dur, duration_s=round(len(audio)/16000, 2))

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
            METRICS["mux_fail"] += 1
            log_event("mux_failed", job_id=job_id, error=str(e))
            output_path = dubbed_wav
            mux_used = False
    dur = round(time.perf_counter() - phase_start, 3)
    JOB_STATUS[job_id]["phases"].append({"phase": "mux", "seconds": dur, "mux_used": mux_used})
    log_event("phase_end", job_id=job_id, phase="mux", mux_used=mux_used, seconds=dur)

    total = round(time.perf_counter() - t0, 3)
    JOB_STATUS[job_id]["state"] = "completed"
    JOB_STATUS[job_id]["total_seconds"] = total
    JOB_STATUS[job_id]["output"] = str(output_path)
    log_event("pipeline_complete", job_id=job_id, output=str(output_path), total_seconds=total)
    return output_path


async def run_pipeline(input_media: Path, src_lang: str = "auto", dst_lang: str = "en", audio_only: bool | None = None) -> tuple[str, Path]:
    """Wrapper that executes the pipeline returning (job_id, output_path)."""
    job_id = uuid.uuid4().hex
    output = await process_media(input_media, src_lang, dst_lang, audio_only=audio_only, job_id=job_id)
    return job_id, output
