# airbnb-clone-project/bookings/models.py

from django.core.exceptions import ValidationError
from django.db import models


class Booking(models.Model):
    """Booking for a property by a guest."""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="bookings"
    )
    guest = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="bookings"
    )
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["check_in_date", "check_out_date"]),
        ]

    def clean(self):
        if self.check_in_date >= self.check_out_date:
            raise ValidationError("Check-out date must be after check-in date.")
        # Overlap detection for the same property (exclude self on update)
        qs = Booking.objects.filter(
            property=self.property, status__in=["pending", "confirmed"]
        )  # active bookings
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        overlap = qs.filter(
            check_in_date__lt=self.check_out_date,
            check_out_date__gt=self.check_in_date,
        ).exists()
        if overlap:
            raise ValidationError(
                "This property is already booked for the selected dates."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Booking #{self.id} - {self.property} by {self.guest}"
