import json
import csv
import io

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.job import Job, JobStatus

router = APIRouter()


@router.get("/{job_id}")
async def get_results(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job.status}",
        )

    results_path = settings.RESULTS_DIR / f"{job_id}.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Results file not found")

    with open(results_path, "r") as f:
        results = json.load(f)

    return results


@router.get("/{job_id}/export")
async def export_results(
    job_id: str,
    format: str = Query("json", regex="^(json|csv)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job.status}",
        )

    results_path = settings.RESULTS_DIR / f"{job_id}.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="Results file not found")

    with open(results_path, "r") as f:
        results = json.load(f)

    if format == "json":
        return StreamingResponse(
            io.BytesIO(json.dumps(results, indent=2).encode()),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=emotion_analysis_{job_id}.json"
            },
        )
    else:
        # CSV export
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "frame_number",
                "timestamp",
                "face_detected",
                "dominant_emotion",
                "confidence",
                "happiness",
                "sadness",
                "anger",
                "fear",
                "disgust",
                "surprise",
                "neutral",
            ]
        )

        # Data rows
        for frame in results.get("frames", []):
            emotions = frame.get("emotions", {})
            writer.writerow(
                [
                    frame.get("frame_number", 0),
                    frame.get("timestamp", 0),
                    frame.get("face_detected", False),
                    frame.get("dominant_emotion", ""),
                    frame.get("confidence", 0),
                    emotions.get("happiness", 0),
                    emotions.get("sadness", 0),
                    emotions.get("anger", 0),
                    emotions.get("fear", 0),
                    emotions.get("disgust", 0),
                    emotions.get("surprise", 0),
                    emotions.get("neutral", 0),
                ]
            )

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=emotion_analysis_{job_id}.csv"
            },
        )
