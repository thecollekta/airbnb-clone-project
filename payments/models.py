# airbnb-clone-project/payments/models.py

from django.db import models


class Payment(models.Model):
    """Payment info linked to a booking."""

    METHOD_CHOICES = (
        ("card", "Card"),
        ("momo", "Mobile Money"),
    )
    STATUS_CHOICES = (
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
    )

    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment {self.transaction_id} ({self.get_status_display()})"
