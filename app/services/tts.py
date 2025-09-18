from __future__ import annotations

from pathlib import Path
import numpy as np
import soundfile as sf
import tempfile
import io
import os
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Voice configurations for different languages
VOICE_CONFIG = {
    'pt': {
        'rate': 160,  # Palavras por minuto
        'volume': 0.9,
        'preferred_voices': [
            'com.apple.speech.synthesis.voice.luciana',  # Luciana (Portuguese)
            'com.apple.speech.synthesis.voice.joana',    # Joana (Portuguese)
            'com.apple.voice.compact.pt-BR.Luciana',     # Compact Portuguese
        ]
    },
    'en': {
        'rate': 180,
        'volume': 0.8,
        'preferred_voices': [
            'com.apple.speech.synthesis.voice.alex',     # Alex (English US)
            'com.apple.speech.synthesis.voice.samantha', # Samantha (English US)
            'com.apple.speech.synthesis.voice.daniel',   # Daniel (English UK)
        ]
    },
    'es': {
        'rate': 170,
        'volume': 0.85,
        'preferred_voices': [
            'com.apple.speech.synthesis.voice.monica',   # Monica (Spanish)
            'com.apple.speech.synthesis.voice.diego',    # Diego (Spanish)
        ]
    }
}

def get_best_voice_for_language(language: str = 'pt'):
    """Encontra a melhor voz disponível para o idioma especificado."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        available_voices = engine.getProperty('voices')
        
        if not available_voices:
            logger.warning("Nenhuma voz encontrada no sistema")
            return None
        
        # Obter configurações para o idioma
        config = VOICE_CONFIG.get(language, VOICE_CONFIG['en'])
        preferred_voices = config.get('preferred_voices', [])
        
        # Primeiro, tentar encontrar uma voz preferida
        for voice in available_voices:
            for preferred in preferred_voices:
                if preferred.lower() in voice.id.lower():
                    logger.info(f"Voz preferida encontrada para {language}: {voice.name} ({voice.id})")
                    return voice
        
        # Se não encontrar voz preferida, procurar por idioma no nome ou ID
        for voice in available_voices:
            voice_info = f"{voice.name} {voice.id}".lower()
            if language == 'pt' and ('port' in voice_info or 'brazil' in voice_info or 'br' in voice_info):
                logger.info(f"Voz portuguesa encontrada: {voice.name} ({voice.id})")
                return voice
            elif language == 'en' and ('english' in voice_info or 'us' in voice_info or 'uk' in voice_info):
                logger.info(f"Voz inglesa encontrada: {voice.name} ({voice.id})")
                return voice
            elif language == 'es' and ('spanish' in voice_info or 'esp' in voice_info):
                logger.info(f"Voz espanhola encontrada: {voice.name} ({voice.id})")
                return voice
        
        # Fallback: usar a primeira voz feminina disponível
        for voice in available_voices:
            if any(name in voice.name.lower() for name in ['female', 'woman', 'samantha', 'alex', 'luciana']):
                logger.info(f"Usando voz fallback: {voice.name} ({voice.id})")
                return voice
        
        # Último recurso: primeira voz disponível
        logger.info(f"Usando primeira voz disponível: {available_voices[0].name}")
        return available_voices[0]
        
    except Exception as e:
        logger.error(f"Erro ao buscar vozes: {e}")
        return None


def synthesize_segment(text: str, language: str = 'pt', sr: int = 16000, duration_per_char: float = 0.05) -> np.ndarray:
    """Sintetiza um segmento de texto usando TTS real (pyttsx3) ou fallback."""
    
    if not text.strip():
        # Sem texto, retorna silêncio curto
        return np.zeros(int(sr * 0.5), dtype=np.float32)
    
    try:
        # Tentar TTS real com pyttsx3
        import pyttsx3
        
        # Criar engine TTS
        engine = pyttsx3.init()
        
        # Obter configurações para o idioma
        config = VOICE_CONFIG.get(language, VOICE_CONFIG['pt'])
        
        # Configurar voz específica para o idioma
        best_voice = get_best_voice_for_language(language)
        if best_voice:
            engine.setProperty('voice', best_voice.id)
        
        # Configurar velocidade (palavras por minuto) baseada no idioma
        engine.setProperty('rate', config['rate'])
        
        # Configurar volume baseado no idioma
        engine.setProperty('volume', config['volume'])
        
        logger.info(f"TTS configurado para {language}: rate={config['rate']}, volume={config['volume']}")
        logger.info(f"Sintetizando: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        
        # Criar arquivo temporário para o áudio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Salvar TTS no arquivo temporário
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            
            # Ler o arquivo gerado
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                data, orig_sr = sf.read(tmp_path)
                
                # Converter para mono se necessário
                if len(data.shape) > 1:
                    data = data.mean(axis=1)
                
                # Resample se necessário
                if orig_sr != sr:
                    import scipy.signal
                    data = scipy.signal.resample(data, int(len(data) * sr / orig_sr))
                
                # Normalizar volume e aplicar compressão suave
                if np.max(np.abs(data)) > 0:
                    # Normalizar
                    data = data / np.max(np.abs(data))
                    
                    # Aplicar compressão suave para tornar o áudio mais consistente
                    data = np.tanh(data * 1.2) * 0.8
                
                logger.info(f"TTS bem-sucedido: {len(data)/sr:.2f}s de áudio gerado")
                return data.astype(np.float32)
            else:
                logger.warning("Arquivo TTS vazio ou não encontrado")
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Erro no pyttsx3: {e}, usando fallback")
    
    # Fallback: gera um tom senoidal breve por caractere (placeholder)
    duration = max(0.3, min(5.0, len(text) * duration_per_char))
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    freq = 220.0
    audio = 0.1 * np.sin(2 * np.pi * freq * t).astype(np.float32)
    logger.warning(f"Usando fallback de tom para '{text[:30]}...'")
    return audio


def synthesize_segments(segments: list[tuple[float, float, str]], target_language: str = 'pt', sr: int = 16000) -> np.ndarray:
    """Concatena áudios por segmento, tentando aproximar o timing."""
    logger.info(f"Sintetizando {len(segments)} segmentos em {target_language}")
    
    out = []
    for i, (start, end, text) in enumerate(segments):
        logger.info(f"[TTS {i+1}/{len(segments)}] Segmento {start:.1f}s-{end:.1f}s: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        seg_audio = synthesize_segment(text, language=target_language, sr=sr)
        target_len = int((end - start) * sr)
        
        if len(seg_audio) < target_len:
            # Adicionar padding se o áudio for mais curto que o esperado
            pad = np.zeros(target_len - len(seg_audio), dtype=np.float32)
            seg_audio = np.concatenate([seg_audio, pad])
        elif len(seg_audio) > target_len:
            # Truncar se o áudio for mais longo que o esperado
            seg_audio = seg_audio[:target_len]
        
        out.append(seg_audio)
    
    if out:
        final_audio = np.concatenate(out)
        logger.info(f"TTS finalizado: {len(final_audio)/sr:.2f}s de áudio total")
        return final_audio
    
    logger.warning("Nenhum áudio gerado, retornando silêncio")
    return np.zeros(1, dtype=np.float32)


# === Experimental OpenVoice Integration ======================================================
def _openvoice_available() -> bool:
    """Return True if OpenVoice models appear to be present and library importable."""
    models_dir = settings.models_dir / "openvoice"
    if not models_dir.exists():
        return False
    if not any(models_dir.glob('*.pt')):
        return False
    try:
        import openvoice  # type: ignore
    except Exception:
        return False
    return True


def synthesize_segments_voice_clone(
    segments: list[tuple[float, float, str]],
    reference_wav: Path,
    target_language: str = 'pt',
    sr: int = 16000
) -> np.ndarray:
    """Attempt to synthesize segments using OpenVoice voice cloning.

    Falls back to standard synthesize_segments if anything fails.
    NOTE: This is a minimal placeholder; a full integration would load proper
    multilingual voice + tone color converter pipelines per OpenVoice docs.
    """
    if not _openvoice_available():
        logger.info("OpenVoice indisponível ou modelos ausentes, fallback para TTS padrão")
        return synthesize_segments(segments, target_language=target_language, sr=sr)

    try:
        import soundfile as sf  # local import to minimize overhead if unavailable
        import numpy as np  # noqa: F401 (already imported but keeps clarity)
        # Pseudo pipeline (placeholder): real implementation would:
        # 1. Extract speaker embedding from reference_wav
        # 2. For cada segmento traduzido gerar mel spectrogram
        # 3. Use vocoder / conversion model to produce waveform preserving timbre
        # For now: call normal TTS then apply simple EQ-like shaping to approximate a distinct timbre.
        base_audio = synthesize_segments(segments, target_language=target_language, sr=sr)
        if len(base_audio) == 0:
            return base_audio

        # Placeholder timbre shaping: high-shelf style attenuation and mild formant-ish emphasis
        import scipy.signal
        b, a = scipy.signal.butter(4, 0.15)
        shaped = scipy.signal.lfilter(b, a, base_audio)
        # Mix original and shaped for a subtle effect
        mixed = 0.6 * base_audio + 0.4 * shaped
        if np.max(np.abs(mixed)) > 0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.9
        logger.info("OpenVoice placeholder aplicado (ajuste tímbrico simples)")
        return mixed.astype(np.float32)
    except Exception as e:
        logger.warning(f"Falha na clonagem de voz experimental: {e}. Usando fallback.")
        return synthesize_segments(segments, target_language=target_language, sr=sr)


def save_wav(wav_path: Path, audio: np.ndarray, sr: int = 16000) -> Path:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(wav_path), audio, sr)
    logger.info(f"Áudio salvo: {wav_path} ({len(audio)/sr:.2f}s)")
    return wav_path
