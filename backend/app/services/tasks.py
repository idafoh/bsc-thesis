import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.job import Job, JobStatus
from app.pipeline.emotion_detector import EmotionDetector

# Sync database session for Celery tasks
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    echo=settings.DEBUG,
)
SyncSessionLocal = sessionmaker(bind=sync_engine)


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int = 0,
    error: str | None = None,
):
    with SyncSessionLocal() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status.value
            job.progress = progress
            if error:
                job.error = error
            if status in (JobStatus.COMPLETED, JobStatus.FAILED):
                job.completed_at = datetime.utcnow()
            db.commit()


@celery_app.task(bind=True)
def process_video_task(self, job_id: str, video_path: str):
    try:
        update_job_status(job_id, JobStatus.PROCESSING)

        detector = EmotionDetector(
            frame_sample_rate=settings.FRAME_SAMPLE_RATE,
            smoothing_window=settings.SMOOTHING_WINDOW_SIZE,
        )

        def progress_callback(progress: int):
            update_job_status(job_id, JobStatus.PROCESSING, progress=progress)
            self.update_state(state="PROGRESS", meta={"progress": progress})

        results = detector.process_video(video_path, progress_callback=progress_callback)

        # Save results
        results_path = settings.RESULTS_DIR / f"{job_id}.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        update_job_status(job_id, JobStatus.COMPLETED, progress=100)

        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        update_job_status(job_id, JobStatus.FAILED, error=str(e))
        raise
