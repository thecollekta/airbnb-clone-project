# airbnb-clone-project/bookings/views.py

from rest_framework import permissions, viewsets

from bookings.models import Booking
from bookings.serializers import BookingSerializer


class IsGuestOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Booking):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.guest_id == getattr(request.user, "id", None)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("property", "guest").all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsGuestOrReadOnly]

    filterset_fields = ["property", "guest", "status", "check_in_date"]
    search_fields = []
    ordering_fields = ["check_in_date", "created_at", "status"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)
