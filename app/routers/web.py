from fastapi import APIRouter, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..config import settings
import io
import numpy as np
import soundfile as sf
from ..services.logs import log_event
from ..services.status import system_status


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


LANG_CHOICES = [
    ("auto", "Auto-detect"),
    ("en", "English"),
    ("pt", "Português"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("it", "Italiano"),
    ("ja", "日本語"),
]


def base_context(request: Request, **extra):
    ctx = {
        "request": request,
        "lang_choices": LANG_CHOICES,
        "status": system_status(),
    }
    ctx.update(extra)
    return ctx


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", base_context(request))


@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    from ..services.status import system_status
    return templates.TemplateResponse("status.html", base_context(request))


@router.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    file: UploadFile,
    src_lang: str = Form("auto"),
    dst_lang: str = Form("en"),
    audio_only: bool = Form(False),
):
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)

    # Save upload
    suffix = Path(file.filename).suffix or ".bin"
    input_path = settings.uploads_dir / f"input{suffix}"
    content = await file.read()
    input_path.write_bytes(content)

    # Kick off processing via API for simplicity (synchronous for now)
    # In production use background tasks or a worker queue
    from ..services.pipeline import process_media

    try:
        result_path = await process_media(input_path, src_lang, dst_lang, audio_only=audio_only)
    except Exception as e:
        # Mostra erro amigável na UI (ex.: problemas de rede/SSL ao baixar modelo)
        return templates.TemplateResponse("index.html", base_context(request, error=str(e)))

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "output_file": result_path.name,
        },
    )


@router.post("/prepare-model", response_class=HTMLResponse)
async def prepare_model(
    request: Request,
    model: str = Form("Systran/faster-whisper-medium"),
    revision: str | None = Form(None),
):
    """Baixa um modelo do Hugging Face para models/ e atualiza ASR_MODEL no .env."""
    try:
        # Importa o utilitário do próprio repo
        from scripts.download_whisper_model import main as dl_main  # type: ignore

        dl_main(model_id=model, revision=revision)
        msg = f"Modelo preparado: {model}. ASR_MODEL atualizado no .env."
        log_event(f"prepare-model success: {model}")
        return templates.TemplateResponse("index.html", base_context(request, success=msg))
    except Exception as e:
        log_event(f"prepare-model error: {e}")
        return templates.TemplateResponse("index.html", base_context(request, error=f"Falha ao preparar o modelo: {e}"))


@router.post("/test-asr", response_class=HTMLResponse)
async def test_asr(request: Request):
    """Gera um WAV curto silencioso e roda ASR para validar o setup/modelo."""
    try:
        # Gera 1 segundo de silêncio a 16 kHz
        sr = 16000
        data = np.zeros(sr, dtype=np.float32)
        buf = io.BytesIO()
        sf.write(buf, data, sr, format="WAV")
        buf.seek(0)

        # Salva temporariamente no uploads
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        test_wav = settings.uploads_dir / "test_silence.wav"
        test_wav.write_bytes(buf.read())

        # Transcreve
        from ..services.asr import transcribe

        segments = transcribe(test_wav, language="en")
        text = " ".join(s.text for s in segments).strip() or "(sem texto reconhecido)"
        msg = f"ASR OK. Segmentos: {len(segments)} | Texto: {text[:120]}"
        log_event("test-asr success")
        return templates.TemplateResponse("index.html", base_context(request, success=msg))
    except Exception as e:
        log_event(f"test-asr error: {e}")
        return templates.TemplateResponse("index.html", base_context(request, error=str(e)))
