# airbnb-clone-project/reviews/models.py

from django.core.exceptions import ValidationError
from django.db import models


class Review(models.Model):
    """Review for a booking written by the guest after a completed stay."""

    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, related_name="review"
    )
    author = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")
        # Ensure review author matches booking guest
        if self.booking and self.author_id and self.booking.guest_id != self.author_id:
            raise ValidationError("Only the guest who booked can review the stay.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Review {self.rating}★ by {self.author}"
