from __future__ import annotations

from pathlib import Path
import asyncio

from .media import extract_audio, mux_video_with_audio, has_ffmpeg
from .asr import transcribe
from .translate import translate_text
from .tts import synthesize_segments, save_wav
from ..config import settings


async def process_media(input_media: Path, src_lang: str, dst_lang: str, audio_only: bool | None = None) -> Path:
    # 1) Extrair áudio mono 16k WAV
    wav_path = input_media.with_suffix(".16k.wav")
    extract_audio(input_media, wav_path, sr=16000)

    # 2) ASR com timestamps
    segments = transcribe(wav_path, language=None if src_lang == "auto" else src_lang)
    print(f"[DEBUG] ASR encontrou {len(segments)} segmentos:")
    for i, seg in enumerate(segments[:3]):  # Mostra apenas os primeiros 3
        print(f"  [{i}] {seg.start:.2f}-{seg.end:.2f}s: '{seg.text}'")

    # 3) Tradução segmento a segmento
    translated_segments: list[tuple[float, float, str]] = []
    for seg in segments:
        # Use src_lang detectado ou configurado para tradução
        source_language = src_lang if src_lang != "auto" else "en"  # Fallback para inglês se auto
        text = translate_text(seg.text, source_language, dst_lang)
        translated_segments.append((seg.start, seg.end, text))
        if len(translated_segments) <= 3:  # Debug apenas os primeiros 3
            print(f"  [TRAD {source_language}->{dst_lang}] '{seg.text}' -> '{text}'")

    # 4) TTS/clonagem de voz (com idioma de destino)
    print(f"[DEBUG] Gerando TTS em {dst_lang} para {len(translated_segments)} segmentos traduzidos")
    audio = synthesize_segments(translated_segments, target_language=dst_lang, sr=16000)
    dubbed_wav = settings.outputs_dir / f"{input_media.stem}.dubbed.wav"
    save_wav(dubbed_wav, audio, sr=16000)

    # 5) Remux com vídeo (se for vídeo) ou retornar áudio
    if audio_only is True or (audio_only is None and not has_ffmpeg()):
        # Sem ffmpeg (ou solicitado), retorna apenas o WAV
        output_path = dubbed_wav
    else:
        output_path = settings.outputs_dir / f"{input_media.stem}.dubbed.mp4"
        try:
            mux_video_with_audio(input_media, dubbed_wav, output_path)
        except Exception:
            # Se não for vídeo, apenas entregue o wav
            output_path = dubbed_wav

    return output_path
