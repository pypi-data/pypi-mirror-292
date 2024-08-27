from typing import Optional, Any
from uuid import UUID

import arrow
import jwt
import loguru
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError

from .common import (
    HEADER_REQ_SIGNATURE_TOKEN,
    get_handler,
    sign_request,
)


def get_client_id(client_token) -> str:
    # Retrieve and decode the client token from headers (without signature validation)
    if not client_token:
        loguru.logger.debug("No client token provided")
        raise AuthenticationFailed("No client token provided")

    unverified_client_payload = jwt.decode(
        client_token, options={"verify_signature": False}
    )
    client_id = unverified_client_payload.get("client_id")

    if not client_id:
        loguru.logger.debug("Invalid client token: missing client_id")
        raise AuthenticationFailed("Invalid client token: missing client_id")

    return client_id


def find_client_key(client_id: str) -> "nftinema.models.ApiClient":
    check_api_client_handler = get_handler(settings.NFTINEMA_CHECK_API_CLIENT_HANDLER)

    # Check client_id via the handler
    check_status, client_key = check_api_client_handler(client_id)
    if not check_status:
        loguru.logger.debug("Client ID is not valid")
        raise AuthenticationFailed(f"Client {client_id} is not valid")
    return client_key


def raise_if_invalid_main_signature(request, client_key, user_jwt, user_uuid, jti, iat, exp):
    signature_token = request.headers.get(HEADER_REQ_SIGNATURE_TOKEN)
    recalculated_token = sign_request(request, client_key, user_jwt, user_uuid, jti, iat, exp)
    if recalculated_token != signature_token:
        msg = f"Invalid signature {recalculated_token} != {signature_token}"
        raise ValidationError(msg)


def raise_if_expire(signature_payload, current_time):
    client_iat = signature_payload.get("iat")
    client_exp = signature_payload.get("exp")

    if not client_iat or not client_exp:
        loguru.logger.debug("Invalid client token: missing iat or exp")
        raise AuthenticationFailed("Invalid client token: missing iat or exp")

    # Validate that the client token has not expired and the duration between iat and exp is less than 5 minutes

    if client_exp < current_time:
        loguru.logger.debug("Client token has expired")
        raise AuthenticationFailed("Client token has expired")

    if (client_exp - client_iat) > 300:  # 300 seconds = 5 minutes
        loguru.logger.debug("Client token's validity period exceeds 5 minutes")
        raise AuthenticationFailed("Client token's validity period exceeds 5 minutes")


def get_user_uuid_from_user_token(
    passport_public_key: str, user_jwt: str, current_time
) -> str:
    # Retrieve and decode the user token from headers using RS256 and the public key

    if not user_jwt:
        loguru.logger.debug("No user token provided")
        raise AuthenticationFailed("No user token provided")

    # Load the public key from settings

    user_payload = jwt.decode(user_jwt, passport_public_key, algorithms=["RS256"])
    user_exp = user_payload.get("exp")

    if not user_exp:
        loguru.logger.debug("Invalid user token: missing exp")
        raise AuthenticationFailed("Invalid user token: missing exp")

    # Validate that the user token has not expired
    if user_exp < current_time:
        loguru.logger.debug("User token has expired")
        raise AuthenticationFailed("User token has expired")

    # Get or create the user based on the UUID from the user token payload
    user_uuid = user_payload.get("user_uuid")
    if not user_uuid:
        loguru.logger.debug("Invalid user token: missing uuid")
        raise AuthenticationFailed("Invalid user token: missing uuid")

    return user_uuid


def authenticate(request):
    passport_public_key = settings.PASSPORT_PUBLIC_KEY
    signature_token = request.headers.get(HEADER_REQ_SIGNATURE_TOKEN)
    # user_jwt = request.headers.get(HEADER_REQ_PASSPORT_TOKEN)
    current_time = arrow.utcnow().int_timestamp

    client_id = get_client_id(signature_token)
    client_key = find_client_key(client_id)
    signature_payload = jwt.decode(
        signature_token, client_key.jwk, algorithms=["HS256"]
    )
    user_jwt = signature_payload["user_jwt"]
    _user_uuid = signature_payload["user_uuid"]
    jti = signature_payload["jti"]
    iat = signature_payload["iat"]
    exp = signature_payload["exp"]

    raise_if_expire(signature_payload, current_time)

    raise_if_invalid_main_signature(request, client_key, user_jwt, _user_uuid, jti, iat, exp)

    user_uuid = get_user_uuid_from_user_token(
        passport_public_key, user_jwt, current_time
    ) if user_jwt else _user_uuid

    User = get_user_model()
    user, created = User.objects.update_or_create(
        username=user_uuid,
        defaults={"uuid": UUID(user_uuid)},
    )
    return user


class DrfAuth(BaseAuthentication):
    def authenticate(self, request):
        try:
            user = authenticate(request)
            return (user, None)
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            ValidationError,
            DjangoValidationError,
        ) as e:
            raise AuthenticationFailed(str(e))


class NinjaAuth:
    def __call__(self, request: HttpRequest) -> Optional[Any]:
        user = authenticate(request)
        # request.user = user
        return user
