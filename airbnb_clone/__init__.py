# airbnb-clone-project/airbnb_clone/__init__.py

from airbnb_clone.celery import app as celery_app

__all__ = ("celery_app",)
