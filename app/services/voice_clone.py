from __future__ import annotations
"""OpenVoice-based experimental voice cloning service.

This module isolates interaction with the OpenVoice CLI / models so that
fallback paths remain clean in tts.py.

Current strategy:
- Detect availability (models + CLI import or executable)
- Provide segment synthesis placeholder; real pipeline wiring is TODO
- Fallback returns None so caller can use standard TTS
"""
from pathlib import Path
import subprocess
import logging
from typing import List, Optional, Dict, Any

import numpy as np
import soundfile as sf
import scipy.signal
from ..config import settings

logger = logging.getLogger(__name__)


def is_openvoice_ready() -> bool:
    if not settings.voice_clone_enabled:
        return False
    mdir = settings.openvoice_models_dir
    if not mdir.exists() or not any(mdir.glob('*.pt')):
        return False
    # Try import path first
    try:
        import openvoice  # type: ignore  # noqa: F401
        return True
    except Exception:
        # Fallback: check CLI presence
        cmd = settings.openvoice_cli_command
        try:
            result = subprocess.run([cmd, '--help'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


def synthesize_segments_voice_clone(
    segments: List[tuple[float, float, str]],
    reference_wav: Path,
    target_language: str = 'pt',
    sr: int = 16000,
) -> np.ndarray | None:
    """Attempt real voice cloning using OpenVoice (placeholder implementation).

    Returns ndarray on success, or None to signal fallback.
    """
    if not is_openvoice_ready():
        return None

    if not reference_wav.exists():
        logger.warning("Reference wav for cloning not found; fallback")
        return None

    try:
        # Placeholder pipeline: concatenate standard TTS later; real integration requires:
        # 1. Speaker embedding extraction from reference_wav
        # 2. Model inference per translated text segment
        # 3. Duration alignment to segment timing
        # For now we just return None so caller uses existing flow.
        logger.info("OpenVoice ready but real synthesis not yet implemented - fallback engaged")
        return None
    except Exception as e:
        logger.error(f"Voice clone error: {e}")
        return None

# ================== Spectral (Fase 1) pseudo-clone ===========================================

def compute_pitch(track: np.ndarray, sr: int) -> float:
    if len(track) == 0:
        return 0.0
    # Autocorrelation-based fundamental estimation (simplified)
    track = track - np.mean(track)
    corr = np.correlate(track, track, mode='full')
    corr = corr[len(corr)//2:]
    # ignore very small lags (below ~70Hz)
    min_lag = int(sr/400)
    max_lag = int(sr/70) if int(sr/70) < len(corr) else len(corr)-1
    segment = corr[min_lag:max_lag]
    if len(segment) == 0:
        return 0.0
    lag = np.argmax(segment) + min_lag
    if lag == 0:
        return 0.0
    return sr/lag


def analyze_reference_voice(reference_wav: Path, sr: int = 16000) -> Optional[Dict[str, Any]]:
    try:
        audio, ref_sr = sf.read(str(reference_wav))
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if ref_sr != sr:
            # Resample
            audio = scipy.signal.resample(audio, int(len(audio) * sr / ref_sr))
        # Basic features
        pitch = compute_pitch(audio, sr)
        energy = float(np.sqrt(np.mean(np.square(audio)))) if len(audio) else 0.0
        # Simple spectral centroid
        freqs, psd = scipy.signal.welch(audio, sr) if len(audio) else (np.array([0.0]), np.array([0.0]))
        centroid = float(np.sum(freqs * psd) / np.sum(psd)) if np.sum(psd) > 0 else 0.0
        profile = {
            'pitch': pitch,
            'energy': energy,
            'centroid': centroid,
        }
        logger.info(f"Reference voice profile: pitch={pitch:.1f}Hz energy={energy:.4f} centroid={centroid:.1f}Hz")
        return profile
    except Exception as e:
        logger.warning(f"Failed to analyze reference voice: {e}")
        return None


def apply_voice_profile(generated: np.ndarray, sr: int, profile: Dict[str, Any]) -> np.ndarray:
    if generated.size == 0:
        return generated
    # Pitch shift via resample scaling
    target_pitch = profile.get('pitch', 0.0)
    if target_pitch > 50:  # crude sanity
        # Estimate current pitch
        current_pitch = compute_pitch(generated, sr)
        if current_pitch > 0:
            ratio_raw = target_pitch / current_pitch
            strength = np.clip(settings.voice_clone_pitch_strength, 0.0, 1.0)
            ratio = 1.0 + (ratio_raw - 1.0) * strength
            if 0.5 < ratio < 2.0 and abs(ratio - 1.0) > 0.02:
                new_len = int(len(generated) / ratio)
                generated = scipy.signal.resample(generated, new_len)
                # Time-stretch back to original length to preserve duration
                generated = scipy.signal.resample(generated, int(len(generated) * ratio))
    # Spectral (brightness) adjustment
    centroid = profile.get('centroid', 0.0)
    if centroid > 0:
        formant_strength = np.clip(settings.voice_clone_formant_strength, 0.0, 1.0)
        # High-shelf style: simple single-pole filter heuristic
        norm_cut = min(0.49, max(0.01, centroid / (sr / 2.0)))
        b, a = scipy.signal.butter(1, norm_cut)
        shaped = scipy.signal.lfilter(b, a, generated)
        generated = (1 - formant_strength) * generated + formant_strength * shaped
    # Normalize
    if np.max(np.abs(generated)) > 0:
        generated = generated / np.max(np.abs(generated)) * 0.9
    return generated.astype(np.float32)


def spectral_clone_segments(
    base_audio: np.ndarray,
    reference_wav: Path,
    sr: int
) -> np.ndarray:
    profile = analyze_reference_voice(reference_wav, sr=sr)
    if not profile:
        return base_audio
    return apply_voice_profile(base_audio, sr, profile)
