# airbnb-clone-project/bookings/serializers.py

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from bookings.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """Serialize Booking fields with validation."""

    class Meta:
        model = Booking
        fields = [
            "id",
            "property",
            "guest",
            "check_in_date",
            "check_out_date",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "guest"]

    def create(self, validated_data):
        """Create a booking and surface model validation errors as 400 responses."""
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, "message_dict", None) or {
                "non_field_errors": e.messages
            }
            raise serializers.ValidationError(detail)

    def update(self, instance, validated_data):
        """Update a booking and surface model validation errors as 400 responses."""
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, "message_dict", None) or {
                "non_field_errors": e.messages
            }
            raise serializers.ValidationError(detail)
