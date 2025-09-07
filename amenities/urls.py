# airbnb-clone-projects/amenities/urls.py

from rest_framework.routers import DefaultRouter

from amenities.views import AmenityViewSet

router = DefaultRouter()
router.register(r"amenities", AmenityViewSet, basename="amenity")

urlpatterns = router.urls
