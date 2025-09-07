# airbnb-clone-project/bookings/tests.py


import datetime as dt

import pytest
from rest_framework.test import APIClient

from tests.factories import AmenityFactory, PropertyFactory, UserFactory


@pytest.mark.django_db
def test_booking_conflict_validation():
    host = UserFactory(user_type="host")
    guest = UserFactory(user_type="guest")
    amenity = AmenityFactory(name="WiFi")

    prop = PropertyFactory(
        host=host, title="Garden view in Kumasi", city="Kumasi", amenities=[amenity]
    )

    client = APIClient()
    client.force_authenticate(guest)

    payload = {
        "property": prop.id,
        "check_in_date": str(dt.date(2025, 10, 10)),
        "check_out_date": str(dt.date(2025, 10, 15)),
        "total_price": "1000.00",
        "status": "confirmed",
    }
    r1 = client.post("/api/v1/bookings/", payload, format="json")
    assert r1.status_code == 201, r1.data

    # Overlapping booking should fail
    payload2 = {
        "property": prop.id,
        "check_in_date": str(dt.date(2025, 10, 12)),
        "check_out_date": str(dt.date(2025, 10, 18)),
        "total_price": "1200.00",
        "status": "pending",
    }
    r2 = client.post("/api/v1/bookings/", payload2, format="json")
    assert r2.status_code in (400, 422)
