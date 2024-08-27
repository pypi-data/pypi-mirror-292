import hashlib
import hmac
from collections import OrderedDict
from importlib import import_module
from typing import Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import jwt
from django.conf import settings

from .structs import ClientKey

HEADER_REQ_SIGNATURE_TOKEN = "X-Request-Signature-Token"
NFTINEMA_CHECK_API_CLIENT_HANDLER = "NFTINEMA_CHECK_API_CLIENT_HANDLER"


def check_api_client(client_id: str) -> (bool, Optional[ClientKey]):
    raise NotImplementedError("Implement this function in your project")


def get_handler(path: str = "libnftinema.common.check_api_client") -> callable:
    module_path, handler_name = path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, handler_name)


def get_url_path(full_url: str) -> str:
    url_parts = urlparse(full_url)
    query_params = OrderedDict(sorted(parse_qsl(url_parts.query)))
    sorted_query = urlencode(query_params)
    new_url_parts = url_parts._replace(query=sorted_query)
    # Rebuild the URL without scheme and netloc
    result_url = urlunparse(new_url_parts._replace(scheme="", netloc=""))
    return result_url


def sign_request(
    request,
    client_key: ClientKey,
    user_jwt: str,
    user_uuid: str,
    jti: str,
    iat: int,
    exp: int,
) -> str:
    full_url = (
        request.build_absolute_uri()
        if hasattr(request, "build_absolute_uri")
        else request.url
    )

    path = get_url_path(full_url)
    path_hash = hmac.new(client_key.k, path.encode("utf-8"), hashlib.sha1)
    body = request.body
    body_hash = hmac.new(client_key.k, body, hashlib.sha1)
    # passport_token_hash = hmac.new(
    #     client_key.k, user_jwt.encode("utf-8"), hashlib.sha1
    # )

    debug_signature: str = "\n".join(
        (
            f"method:{request.method}",
            f"path:{path}",
            f"body:{body}",
            f"body_hash:{body_hash.hexdigest()}",
        )
    )

    signature = hmac.new(client_key.k, debug_signature.encode("utf-8"), hashlib.sha1)

    payload = {
        "client_id": client_key.kid,
        "user_jwt": user_jwt,
        "user_uuid": user_uuid,
        "iat": iat,
        "exp": exp,
        "jti": jti,
        "signature": signature.hexdigest(),
        "debug_signature": debug_signature,
    }
    token = jwt.encode(payload, client_key.jwk, algorithm="HS256")

    return token


def get_client_key() -> ClientKey:
    return settings.NFTINEMA_CLIENT_KEY
