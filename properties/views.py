# airbnb-clone-project/properties/views.py

from rest_framework import permissions, viewsets

from properties.models import Property
from properties.serializers import PropertySerializer


class IsHostOrReadOnly(permissions.BasePermission):
    """Only hosts (owner) can modify their own property; others read-only."""

    def has_object_permission(self, request, view, obj: Property):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.host_id == getattr(request.user, "id", None)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = (
        Property.objects.select_related("host").prefetch_related("amenities").all()
    )
    serializer_class = PropertySerializer
    # Public read access; write restricted to authenticated owner
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsHostOrReadOnly]

    filterset_fields = ["city", "country", "bedrooms", "amenities"]
    search_fields = ["title", "description", "city"]
    ordering_fields = ["price_per_night", "created_at", "bedrooms"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
