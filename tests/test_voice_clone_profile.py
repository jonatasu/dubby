import numpy as np
from pathlib import Path
from app.services.voice_clone import analyze_reference_voice, apply_voice_profile


def test_analyze_reference_voice_and_apply(tmp_path: Path):
    # Cria um wav sintético simples (seno + harmônico) e salva
    import soundfile as sf
    sr = 16000
    t = np.linspace(0, 1.0, sr, endpoint=False)
    base = 0.5 * np.sin(2 * np.pi * 180 * t) + 0.2 * np.sin(2 * np.pi * 360 * t)
    ref_path = tmp_path / "ref.wav"
    sf.write(str(ref_path), base, sr)

    profile = analyze_reference_voice(ref_path, sr=sr)
    assert profile is not None
    assert profile['pitch'] > 100
    assert profile['energy'] > 0

    # Gera um outro sinal para modulação
    gen = 0.4 * np.sin(2 * np.pi * 140 * t)
    out = apply_voice_profile(gen, sr, profile)
    assert out.shape == gen.shape
    # Garantir mudança mínima (ex: energia ou diferença RMS)
    diff = float(np.sqrt(np.mean((out - gen) ** 2)))
    assert diff > 0.0005
