from pathlib import Path
from app.services.voice_clone import is_openvoice_ready, synthesize_segments_voice_clone


def test_openvoice_not_ready_without_models(tmp_path: Path):
    # Garantir que diretório padrão não existe no ambiente de teste isolado
    # (Se existir localmente com modelos reais, este teste poderá precisar de isolamento extra)
    assert is_openvoice_ready() is False

    segments = [(0.0, 1.0, "hello world")]
    ref = tmp_path / "ref.wav"
    # Cria wav vazio falso como referência inexistente real
    ref.write_bytes(b"fake")

    result = synthesize_segments_voice_clone(segments, ref, target_language="pt")
    # Como não há modelos e função retorna None para fallback
    assert result is None
