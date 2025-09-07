# airbnb-clone-project/properties/models.py

from django.conf import settings
from django.db import models


class Property(models.Model):
    """Property listing model."""

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.PositiveIntegerField(default=1)
    # Simple location for now; can be upgraded to PostGIS later
    city = models.CharField(max_length=100, help_text="City e.g., Accra, Kumasi")
    country = models.CharField(max_length=100, default="Ghana")
    amenities = models.ManyToManyField(
        "amenities.Amenity", blank=True, related_name="properties"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["price_per_night"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} - {self.city}, {self.country}"
