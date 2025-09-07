"""
URL configuration for airbnb_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


def health_view(_request):
    """Simple health check endpoint for readiness/liveness probes."""
    return JsonResponse({"status": "ok", "service": "airbnb_clone"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                # Health check
                path("health/", health_view, name="health"),
                # OpenAPI schema and docs
                path("schema/", SpectacularAPIView.as_view(), name="schema"),
                path(
                    "schema/swagger-ui/",
                    SpectacularSwaggerView.as_view(url_name="schema"),
                    name="swagger-ui",
                ),
                path(
                    "schema/redoc/",
                    SpectacularRedocView.as_view(url_name="schema"),
                    name="redoc",
                ),
                # Auth (JWT)
                path(
                    "auth/",
                    include(
                        [
                            path(
                                "token/",
                                TokenObtainPairView.as_view(),
                                name="token_obtain_pair",
                            ),
                            path(
                                "token/refresh/",
                                TokenRefreshView.as_view(),
                                name="token_refresh",
                            ),
                            path(
                                "token/verify/",
                                TokenVerifyView.as_view(),
                                name="token_verify",
                            ),
                            # Accounts app URLs for auth/
                            path("", include("accounts.urls")),
                        ]
                    ),
                ),
                # App routers
                path("", include("users.urls")),
                path("", include("amenities.urls")),
                path("", include("properties.urls")),
                path("", include("bookings.urls")),
                path("", include("payments.urls")),
                path("", include("reviews.urls")),
            ]
        ),
    ),
]
