import platform

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "emotion_detection",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.tasks"],
)

# Use 'solo' pool on macOS to avoid fork() issues with OpenGL/MediaPipe
worker_pool = "solo" if platform.system() == "Darwin" else "prefork"

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    worker_pool=worker_pool,
)
