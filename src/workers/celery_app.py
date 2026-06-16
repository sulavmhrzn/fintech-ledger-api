from celery import Celery
from celery.schedules import crontab

from src.config.settings import settings

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "fintech_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["src.workers.tasks"],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "delete-expired-tokens-every-hour": {
        "task": "cleanup_expired_otp_tokens",
        "schedule": crontab(minute=0),
    }
}
