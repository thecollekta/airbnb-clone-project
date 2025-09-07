# airbnb-clone-project/airbnb_clone/celery.py

import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airbnb_clone.settings")

app = Celery("airbnb_clone")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure task routes if needed
app.conf.task_routes = {
    "payments.tasks.*": {"queue": "payments"},
    "bookings.tasks.*": {"queue": "bookings"},
    "emails.tasks.*": {"queue": "emails"},
}

# Configure task time limits
app.conf.task_time_limit = 30 * 60  # 30 minutes
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes

# Configure retries
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_track_started = True

# Configure result backend
app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# Configure broker connection
app.conf.broker_connection_retry_on_startup = True

# Setup periodic tasks
app.conf.beat_schedule = {
    "cleanup-expired-bookings": {
        "task": "bookings.tasks.cleanup_expired_bookings",
        "schedule": 3600.0,  # Run every hour
    },
    "send-booking-reminders": {
        "task": "bookings.tasks.send_booking_reminders",
        "schedule": 86400.0,  # Run daily
    },
}

# Add this to ensure the Celery app is properly configured
app.conf.update(worker_prefetch_multiplier=1, worker_max_tasks_per_child=100)

if __name__ == "__main__":
    app.start()
