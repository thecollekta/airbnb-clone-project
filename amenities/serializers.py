# airbnb-clone-project/amenities/serializers.py

from rest_framework import serializers

from amenities.models import Amenity


class AmenitySerializer(serializers.ModelSerializer):
    """Serialize Amenity fields for API use."""

    class Meta:
        model = Amenity
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
