from unittest.mock import MagicMock, patch

import jwt
import pytest
from django.conf import settings
from requests import Session, Response, PreparedRequest

from libnftinema.client import APIClient
from libnftinema.common import HEADER_REQ_SIGNATURE_TOKEN, get_client_key


@pytest.fixture()
def api_client():
    from django.conf import settings

    return APIClient(
        base_url="http://testserver/api",
        client_key=get_client_key(),
        user_jwt=settings.USER_JWT,
    )


def test_post_request_signature(api_client):
    with patch.object(Session, "send", wraps=Session().send) as mock_send:
        # Arrange
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_send.return_value = mock_response

        data = {"key": "value"}
        endpoint = "/test-endpoint"

        # Act
        response = api_client.spost(endpoint, data)

        # Assert
        assert response.status_code == 200
        assert mock_send.call_count == 1

        # Inspect the actual PreparedRequest object that was sent
        prepared_request: PreparedRequest = mock_send.call_args[0][0]

        # Extract the signature token from the headers
        signature_jwt = prepared_request.headers.get(HEADER_REQ_SIGNATURE_TOKEN)
        assert (
            signature_jwt is not None
        ), "Signature JWT token should be present in the headers"

        payload = jwt.decode(signature_jwt, get_client_key().jwk, algorithms=["HS256"])

        assert payload["user_jwt"] == settings.USER_JWT
        assert payload["client_id"] == get_client_key().kid
