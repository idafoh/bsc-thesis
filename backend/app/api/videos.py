import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.job import Job, JobStatus
from app.services.tasks import process_video_task

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm"}
MIME_TYPES = {
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
}


@router.get("/{job_id}")
async def get_video(job_id: str, db: AsyncSession = Depends(get_db)):
    """Stream the video file for a given job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Find the video file
    video_path = None
    for ext in ALLOWED_EXTENSIONS:
        path = settings.UPLOAD_DIR / f"{job_id}{ext}"
        if path.exists():
            video_path = path
            break

    if not video_path:
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=video_path,
        media_type=MIME_TYPES.get(video_path.suffix, "video/mp4"),
        filename=job.filename,
    )


MAX_FILE_SIZE = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_VIDEO_SIZE_MB}MB",
        )

    # Generate job ID and save file
    job_id = str(uuid.uuid4())
    file_path = settings.UPLOAD_DIR / f"{job_id}{file_ext}"

    with open(file_path, "wb") as f:
        f.write(content)

    # Create job record
    job = Job(
        id=job_id,
        filename=file.filename,
        status=JobStatus.PENDING.value,
    )
    db.add(job)
    await db.commit()

    # Queue processing task
    task = process_video_task.delay(job_id, str(file_path))

    # Update job with task ID
    job.celery_task_id = task.id
    await db.commit()

    return {
        "job_id": job_id,
        "message": "Video uploaded successfully. Processing started.",
    }
