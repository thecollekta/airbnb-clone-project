# airbnb-clone-project/payments/tests.py


import pytest
from rest_framework.test import APIClient

from tests.factories import AmenityFactory, PropertyFactory, UserFactory


@pytest.mark.django_db
def test_payment_momo():
    host = UserFactory(user_type="host")
    guest = UserFactory(user_type="guest")
    amenity = AmenityFactory(name="Generator")
    prop = PropertyFactory(
        host=host, title="Osu Studio", city="Accra", amenities=[amenity]
    )

    client = APIClient()
    client.force_authenticate(guest)

    # Create booking via API to follow normal workflow
    r = client.post(
        "/api/v1/bookings/",
        {
            "property": prop.id,
            "check_in_date": "2025-11-01",
            "check_out_date": "2025-11-05",
            "total_price": "1000.00",
            "status": "confirmed",
        },
        format="json",
    )
    assert r.status_code == 201
    booking_id = r.data["id"]

    # Create payment using MoMo
    r2 = client.post(
        "/api/v1/payments/",
        {
            "booking": booking_id,
            "amount": "1000.00",
            "payment_method": "momo",
            "transaction_id": "MTN-0001",
            "status": "succeeded",
        },
        format="json",
    )
    assert r2.status_code == 201, r2.data
    assert r2.data["payment_method"] == "momo"
