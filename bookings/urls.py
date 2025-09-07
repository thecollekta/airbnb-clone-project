# airbnb-clone-project/bookings/urls.py

from rest_framework.routers import DefaultRouter

from bookings.views import BookingViewSet

router = DefaultRouter()
router.register(r"bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
