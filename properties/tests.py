# airbnb-clone-project/properties/tests.py


import pytest
from rest_framework.test import APIClient

from tests.factories import AmenityFactory, UserFactory


@pytest.mark.django_db
def test_create_property_with_amenities():
    host = UserFactory(user_type="host")
    a1 = AmenityFactory(name="Air Conditioning")
    a2 = AmenityFactory(name="Parking")

    client = APIClient()
    client.force_authenticate(host)

    payload = {
        "title": "Cozy apartment in East Legon",
        "description": "Near Accra Mall",
        "price_per_night": "350.00",
        "bedrooms": 2,
        "city": "Accra",
        "country": "Ghana",
        "amenity_ids": [a1.id, a2.id],
    }
    resp = client.post("/api/v1/properties/", payload, format="json")
    assert resp.status_code == 201, resp.data
    assert resp.data["city"] == "Accra"
    assert len(resp.data["amenities"]) == 2
