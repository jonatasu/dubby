from __future__ import annotations

from typing import Optional

from ..config import settings


def translate_text(text: str, src_lang: str, dst_lang: str) -> str:
    """
    Placeholder de tradução: retorna o texto original.
    Integração com Argos/Marian pode ser habilitada depois (fora do requirements padrão).
    """
    return text if src_lang == dst_lang or dst_lang == "auto" else text
