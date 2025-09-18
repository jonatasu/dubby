from fastapi import APIRouter, File, UploadFile, Response, HTTPException
from ..services.upload_validation import validate_upload
from ..services.pipeline import run_pipeline, JOB_STATUS, METRICS
from ..services.status import system_status


router = APIRouter()


@router.post("/process")
async def process_media(file: UploadFile = File(...)):
    data = await file.read()
    target_path = validate_upload(file, data)
    with open(target_path, "wb") as f:
        f.write(data)
    try:
        job_id, output_file = await run_pipeline(target_path)
    except HTTPException:
        raise
    except Exception as e:
        from ..services.logs import log_event
        log_event("pipeline_failure", error=str(e))
        raise HTTPException(status_code=500, detail="Processing failed")
    headers = {"X-Job-ID": job_id}
    return Response(content=output_file.read_bytes(), media_type="application/octet-stream", headers=headers)


@router.get("/status")
async def status():
    data = system_status()
    # anexar métricas e últimos jobs (limit 5)
    jobs = list(JOB_STATUS.items())[-5:]
    data["metrics"] = METRICS
    data["recent_jobs"] = [{"job_id": jid, **info} for jid, info in jobs]
    return data


@router.get("/job/{job_id}")
async def job_status(job_id: str):
    info = JOB_STATUS.get(job_id)
    if not info:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **info}
