import jwt
import pytest
from django.conf import settings
from django.urls import reverse

from libnftinema.client import APIClient
from libnftinema.common import get_client_key


@pytest.fixture()
def api_client():
    from django.conf import settings

    return APIClient(
        base_url="http://testserver",
        client_key=get_client_key(),
        user_jwt=settings.USER_JWT,
        is_test=True,
    )


@pytest.mark.django_db
def test_simple_get(api_client):
    url = reverse("simple-get")
    response = api_client.get(url)
    assert response.status_code == 200, response.content


@pytest.mark.django_db
def test_raise_if_not_signed(api_client):
    url = reverse("secure-post")
    response = api_client.post(url, {"x": 1})
    assert response.status_code == 403, response.content
    assert response.json() == {"detail": "No client token provided"}, response.content


@pytest.mark.django_db
def test_secure_post_view(api_client):
    url = reverse("secure-post")
    data = {"key": "value"}

    response = api_client.spost(url, data)

    assert response.status_code == 200, response.content

    d = response.data

    assert "message" in d
    assert "data" in d
    assert "user" in d
    assert d["message"] == "Data received"
    assert d["data"] == data
    assert d["user"] is not None

    user_jwt = jwt.decode(
        settings.USER_JWT, settings.PASSPORT_PUBLIC_KEY, algorithms=["RS256"]
    )

    assert d["user"]["uuid"] == user_jwt["user_uuid"]
