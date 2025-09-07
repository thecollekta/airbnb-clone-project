# airbnb-clone-project/common/apps.py

import os
import sys

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate


def run_seed(sender, **kwargs):
    """Run the seed command after migrations are complete."""
    if not settings.DEBUG or "runserver" not in sys.argv:
        return

    # When autoreload is enabled, Django starts the process twice.
    # RUN_MAIN is "true" only in the reloader child process
    if os.environ.get("RUN_MAIN") != "true":
        return

    # Light-weight existence check to avoid reseeding every run
    from amenities.models import Amenity
    from properties.models import Property

    if Amenity.objects.exists() or Property.objects.exists():
        return

    # Create a reasonable baseline with payments and reviews enabled
    call_command(
        "seed",
        amenities=15,
        hosts=5,
        guests=15,
        properties=20,
        bookings=25,
        payments=True,
        reviews=True,
    )


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        """Connect the post_migrate signal to run the seed command."""

        # Only run in development
        if not settings.DEBUG:
            return

        # Connect to post_migrate signal instead of running directly in ready()
        post_migrate.connect(run_seed, sender=self, dispatch_uid="common.apps.run_seed")
