from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from huggingface_hub import snapshot_download


def update_env(asr_model_path: str, env_path: Path) -> None:
    lines: list[str]
    if env_path.exists():
        lines = env_path.read_text().splitlines()
    else:
        lines = []
    found = False
    for i, line in enumerate(lines):
        if line.startswith("ASR_MODEL="):
            lines[i] = f"ASR_MODEL={asr_model_path}"
            found = True
            break
    if not found:
        lines.append(f"ASR_MODEL={asr_model_path}")
    env_path.write_text("\n".join(lines) + "\n")


def main(model_id: str = "Systran/faster-whisper-medium", revision: Optional[str] = None) -> None:
    root = Path(__file__).resolve().parents[1]
    models_dir = root / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    print(f"Baixando modelo '{model_id}' para {models_dir} ...")
    local_dir = snapshot_download(
        repo_id=model_id,
        revision=revision or "main",
        local_dir=models_dir,
        local_dir_use_symlinks=False,
        max_workers=8,
    )

    # Normalizar caminho em formato sem barras para usar como ASR_MODEL
    # Ex.: models/Systran__faster-whisper-medium
    rel = Path(local_dir).resolve().relative_to(root)
    normalized = str(rel).replace("/", "__")
    # Guardar dentro de models/ com nome normalizado (se necessário)
    target = models_dir / normalized
    if not target.exists():
        os.rename(local_dir, target)

    # Atualizar .env
    update_env(asr_model_path=str(target.relative_to(root)), env_path=root / ".env")
    print(f"Pronto. ASR_MODEL atualizado no .env para: {target.relative_to(root)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Baixa um modelo Whisper do Hugging Face para 'models/' e atualiza .env")
    parser.add_argument("--model", default="Systran/faster-whisper-medium", help="Repo id do modelo (ex.: Systran/faster-whisper-medium)")
    parser.add_argument("--revision", default=None, help="Revisão/branch/tag (default: main)")
    args = parser.parse_args()
    main(model_id=args.model, revision=args.revision)
