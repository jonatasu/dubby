from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse
from pathlib import Path
from ..config import settings
from ..services.pipeline import process_media
from ..services.status import system_status


router = APIRouter()


@router.post("/process")
async def process(
    file: UploadFile,
    src_lang: str = Form("auto"),
    dst_lang: str = Form("en"),
):
    suffix = Path(file.filename).suffix or ".bin"
    input_path = settings.uploads_dir / f"input{suffix}"
    input_path.write_bytes(await file.read())

    result_path = await process_media(input_path, src_lang, dst_lang)
    return FileResponse(result_path)


@router.get("/status")
async def status():
    return system_status()
