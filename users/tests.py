# airbnb-clone-project/users/tests.py


import pytest
from rest_framework.test import APIClient

from accounts.models import User


@pytest.mark.django_db
def test_users_me_get_and_update():
    user = User.objects.create_user(
        email="naa@example.com", password="pass1234", first_name="Naa"
    )
    client = APIClient()
    client.force_authenticate(user)

    r = client.get("/api/v1/users/me/")
    assert r.status_code == 200
    assert r.data["email"].startswith("naa@")

    r2 = client.patch("/api/v1/users/me/", {"first_name": "Naa Dede"}, format="json")
    assert r2.status_code == 200
    assert r2.data["first_name"] == "Naa Dede"
