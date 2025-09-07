# airbnb-clone-project/properties/serializers.py

from rest_framework import serializers

from properties.models import Property


class PropertySerializer(serializers.ModelSerializer):
    """Serialize property fields, exposing amenity IDs list."""

    amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        source="amenities",
        queryset=Property._meta.get_field("amenities").remote_field.model.objects.all(),
    )

    class Meta:
        model = Property
        fields = [
            "id",
            "host",
            "title",
            "description",
            "price_per_night",
            "bedrooms",
            "city",
            "country",
            "amenities",
            "amenity_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "host"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["amenities"] = [a.id for a in instance.amenities.all()]
        return data
