from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery(
    "vulnguard",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.ingestion.tasks",
        "app.matching.tasks",
        "app.ml.tasks",
        "app.graph.tasks",
    ],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# ── Scheduled Tasks ──
celery.conf.beat_schedule = {
    "ingest-nvd-cves": {
        "task": "app.ingestion.tasks.ingest_nvd_cves",
        "schedule": crontab(hour="*/6", minute=0),
    },
    "ingest-cisa-kev": {
        "task": "app.ingestion.tasks.ingest_cisa_kev",
        "schedule": crontab(hour="*/12", minute=15),
    },
    "ingest-epss-scores": {
        "task": "app.ingestion.tasks.ingest_epss_scores",
        "schedule": crontab(hour=2, minute=0),
    },
    "run-vulnerability-matching": {
        "task": "app.matching.tasks.run_matching",
        "schedule": crontab(hour="*/6", minute=30),
    },
    "rebuild-attack-graph": {
        "task": "app.graph.tasks.rebuild_graph",
        "schedule": crontab(hour=3, minute=0),
    },
    "retrain-ml-model": {
        "task": "app.ml.tasks.retrain_model",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),  # weekly
    },
}
