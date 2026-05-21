"""Celery tasks for background processing."""
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create celery app
celery_app = Celery(
    "secureexam",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 min max
    worker_prefetch_multiplier=4,
)


@celery_app.task(name="cleanup_old_sessions")
def cleanup_old_sessions():
    """Clean up old exam sessions."""
    # Placeholder for cleanup task
    return {"deleted": 0}


@celery_app.task(name="send_notification")
def send_notification(user_id: int, message: str):
    """Send notification to user."""
    # Placeholder for notification task
    return {"sent_to": user_id}


@celery_app.task(name="generate_report")
def generate_report(tenant_id: int, exam_id: int):
    """Generate exam report."""
    # Placeholder for report generation
    return {"exam_id": exam_id, "status": "generated"}


# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-sessions-daily": {
        "task": "cleanup_old_sessions",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}