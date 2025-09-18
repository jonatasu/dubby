from __future__ import annotations
from fastapi import HTTPException, UploadFile
from pathlib import Path
from .logs import log_event
from ..config import settings


def validate_upload(file: UploadFile, data: bytes) -> Path:
    """Validate uploaded file against size and extension constraints.

    Returns a safe target path (randomized name) if valid, else raises HTTPException.
    """
    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = len(data)
    if size == 0:
        raise HTTPException(status_code=400, detail="Empty file upload")
    if size > max_bytes:
        log_event("upload_reject", reason="size", size=size, limit=max_bytes)
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb} MB limit")

    allowed = {ext.strip().lower() for ext in settings.allowed_upload_extensions.split(',') if ext.strip()}
    orig_name = file.filename or "uploaded.bin"
    ext = Path(orig_name).suffix.lower()
    if ext not in allowed:
        log_event("upload_reject", reason="extension", ext=ext)
        raise HTTPException(status_code=415, detail=f"Extension {ext or '(none)'} not allowed")

    # Sanitize & create unique name
    import uuid
    safe_name = f"{uuid.uuid4().hex}{ext}"
    target = settings.uploads_dir / safe_name
    return target
