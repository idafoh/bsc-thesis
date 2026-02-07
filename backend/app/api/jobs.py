from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.job import Job

router = APIRouter()


@router.get("")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).order_by(Job.created_at.desc()))
    jobs = result.scalars().all()
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job.to_dict()


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    from app.core.celery_app import celery_app
    from app.core.config import settings

    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Cancel Celery task if running
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    # Delete uploaded file
    for ext in [".mp4", ".avi", ".mov", ".webm"]:
        file_path = settings.UPLOAD_DIR / f"{job_id}{ext}"
        if file_path.exists():
            file_path.unlink()

    # Delete results file
    results_path = settings.RESULTS_DIR / f"{job_id}.json"
    if results_path.exists():
        results_path.unlink()

    # Delete job record
    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted successfully"}
