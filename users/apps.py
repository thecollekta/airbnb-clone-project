# airbnb-clone-project/users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    label = "users_api"
