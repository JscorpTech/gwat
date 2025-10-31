from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check_fail_chargers": {
        "task": "core.apps.api.tasks.charger.check_fail_chargers",
        "schedule": crontab(minute="*/5"),
    },
}
