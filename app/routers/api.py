from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse
import uuid
from pathlib import Path
from ..config import settings
from ..services.pipeline import process_media, JOB_STATUS, METRICS
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

    job_id = uuid.uuid4().hex
    result_path = await process_media(input_path, src_lang, dst_lang, job_id=job_id)
    resp = FileResponse(result_path)
    resp.headers["X-Job-ID"] = job_id
    return resp


@router.get("/status")
async def status():
    data = system_status()
    # anexar métricas e últimos jobs (limit 5)
    jobs = list(JOB_STATUS.items())[-5:]
    data["metrics"] = METRICS
    data["recent_jobs"] = [{"job_id": jid, **info} for jid, info in jobs]
    return data
