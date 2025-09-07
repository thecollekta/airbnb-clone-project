# airbnb-clone-project/amenities/models.py

from django.db import models


class Amenity(models.Model):
    """Amenity model representing a feature available at a property."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
