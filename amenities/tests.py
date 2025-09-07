# airbnb-clone-project/amenities/tests.py


import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory


@pytest.mark.django_db
def test_create_and_list_amenities():
    user = UserFactory(user_type="host")
    client = APIClient()
    client.force_authenticate(user)

    # Create
    resp = client.post(
        "/api/v1/amenities/",
        {"name": "WiFi", "description": "Fast internet"},
        format="json",
    )
    assert resp.status_code == 201
    amenity_id = resp.data["id"]

    # List
    resp = client.get("/api/v1/amenities/")
    assert resp.status_code == 200
    # Handle both paginated and non-paginated responses
    data = (
        resp.data.get("results")
        if isinstance(resp.data, dict) and "results" in resp.data
        else resp.data
    )
    assert any(a["id"] == amenity_id for a in data)
