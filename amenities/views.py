# airbnb-clone-project/amenities/views.py

from rest_framework import permissions, viewsets

from amenities.models import Amenity
from amenities.serializers import AmenitySerializer


class AmenityViewSet(viewsets.ModelViewSet):
    """CRUD for amenities."""

    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["name"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
