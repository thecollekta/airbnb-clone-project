# airbnb-clone-project/reviews/tests.py


import pytest
from rest_framework.test import APIClient

from accounts.models import User
from amenities.models import Amenity
from properties.models import Property


@pytest.mark.django_db
def test_review_author_must_be_booking_guest():
    host = User.objects.create_user(
        email="kofi@example.com", password="pass1234", user_type="host"
    )
    guest = User.objects.create_user(
        email="yaw2@example.com", password="pass1234", user_type="guest"
    )
    other = User.objects.create_user(
        email="notguest@example.com", password="pass1234", user_type="guest"
    )
    amenity = Amenity.objects.create(name="Pool")

    prop = Property.objects.create(
        host=host,
        title="Cantonments House",
        description="Secure area",
        price_per_night="500.00",
        bedrooms=4,
        city="Accra",
        country="Ghana",
    )
    prop.amenities.add(amenity)

    client = APIClient()
    client.force_authenticate(guest)

    # Create booking
    r = client.post(
        "/api/v1/bookings/",
        {
            "property": prop.id,
            "check_in_date": "2025-12-20",
            "check_out_date": "2025-12-25",
            "total_price": "2500.00",
            "status": "confirmed",
        },
        format="json",
    )
    assert r.status_code == 201
    booking_id = r.data["id"]

    # Attempt to create review with a different user
    client.force_authenticate(other)
    r2 = client.post(
        "/api/v1/reviews/",
        {"booking": booking_id, "rating": 5, "comment": "Great stay!"},
        format="json",
    )
    assert r2.status_code in (400, 403)
