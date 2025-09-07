# airbnb-clone-project/reviews/serializers.py

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize Review fields and report validation errors properly."""

    class Meta:
        model = Review
        fields = ["id", "booking", "author", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at", "author"]

    def create(self, validated_data):
        """Create a review and surface model validation errors as 400 responses."""
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, "message_dict", None) or {
                "non_field_errors": e.messages
            }
            raise serializers.ValidationError(detail)

    def update(self, instance, validated_data):
        """Update a review and surface model validation errors as 400 responses."""
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, "message_dict", None) or {
                "non_field_errors": e.messages
            }
            raise serializers.ValidationError(detail)
