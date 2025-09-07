# airbnb-clone-project/users/urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import MeViewSet

app_name = "users"

# Create a router for any future API endpoints
router = DefaultRouter()

# Manually define the URLs for the MeViewSet
urlpatterns = [
    # GET /api/v1/users/me/ - Get current user profile
    # PATCH /api/v1/users/me/ - Update current user profile
    path(
        "me/",
        MeViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "put": "update",
            }
        ),
        name="me",
    ),
    # GET /api/v1/users/me/change-password/ - Change password
    path(
        "me/change-password/",
        MeViewSet.as_view({"post": "change_password"}),
        name="change-password",
    ),
]

# Include any router URLs
urlpatterns += router.urls
