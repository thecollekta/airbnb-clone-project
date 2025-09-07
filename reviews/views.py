# airbnb-clone-project/reviews/views.py

from rest_framework import permissions, viewsets

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Review):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == getattr(request.user, "id", None)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("booking", "author").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    filterset_fields = ["rating", "booking", "author"]
    search_fields = ["comment"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
