import uuid

import arrow
from django.test import Client as DjangoTestClient
from requests import Request, Session

from .common import HEADER_REQ_SIGNATURE_TOKEN, sign_request
from .structs import ClientKey


class APIClient:
    base_url: str
    user_jwt: str
    user_uuid: str
    client_key: ClientKey
    is_test: bool
    jti: str
    iat: int
    exp: int

    def __init__(
        self,
        base_url: str,
        client_key: ClientKey,
        user_jwt: str = None,
        user_uuid: str = None,
        jti: str = None,
        iat: int = None,
        exp: int = None,
        is_test: bool = False,
    ):
        self.base_url = base_url
        self.user_jwt = user_jwt
        self.user_uuid = user_uuid
        self.client_key = client_key
        self.is_test = is_test
        if self.is_test:
            self.django_client = DjangoTestClient()
        self.jti = str(uuid.uuid4()) if not jti else jti
        self.iat = arrow.utcnow().int_timestamp if not iat else iat
        self.exp = arrow.utcnow().shift(minutes=5).int_timestamp if not exp else exp

    def _prepare_signed_request(self, method, endpoint, headers=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        request = Request(method, url, headers=headers, **kwargs)
        prepared_request = request.prepare()
        signature_jwt = sign_request(
            prepared_request,
            client_key=self.client_key,
            user_jwt=self.user_jwt,
            user_uuid = self.user_uuid,
            jti=self.jti,
            iat=self.iat,
            exp=self.exp,
        )
        print(f"Generated signature_jwt: {signature_jwt}")  # Debugging line
        prepared_request.headers[HEADER_REQ_SIGNATURE_TOKEN] = signature_jwt
        print(
            f"Headers after adding signature: {prepared_request.headers}"
        )  # Debugging line
        return prepared_request

    def _send_signed_request(self, method, endpoint, headers=None, **kwargs):
        prepared_request = self._prepare_signed_request(
            method, endpoint, headers, **kwargs
        )
        if self.is_test:
            client_method = getattr(self.django_client, method.lower())
            return client_method(
                prepared_request.path_url,
                prepared_request.body,
                content_type="application/json",
                headers=dict(prepared_request.headers),
            )

        with Session() as session:
            return session.send(prepared_request)

    def _send_unsigned_request(self, method, endpoint, headers=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        request = Request(method, url, headers=headers, **kwargs)
        prepared_request = request.prepare()

        if self.is_test:
            client_method = getattr(self.django_client, method.lower())
            return client_method(
                prepared_request.path_url,
                prepared_request.body,
                content_type="application/json",
                headers=dict(prepared_request.headers),
            )

        with Session() as session:
            return session.send(prepared_request)

    def request(self, method, endpoint, data=None, params=None, headers=None):
        return self._send_signed_request(
            method, endpoint, headers=headers, json=data, params=params
        )

    def post(self, endpoint, data=None, headers=None):
        return self._send_unsigned_request("POST", endpoint, headers=headers, json=data)

    def put(self, endpoint, data=None, headers=None):
        return self._send_unsigned_request("PUT", endpoint, headers=headers, json=data)

    def patch(self, endpoint, data=None, headers=None):
        return self._send_unsigned_request(
            "PATCH", endpoint, headers=headers, json=data
        )

    def get(self, endpoint, params=None, headers=None):
        return self._send_unsigned_request(
            "GET", endpoint, headers=headers, params=params
        )

    def head(self, endpoint, headers=None):
        return self._send_unsigned_request("HEAD", endpoint, headers=headers)

    def spost(self, endpoint, data, headers=None):
        return self.request("POST", endpoint, data=data, headers=headers)

    def sput(self, endpoint, data, headers=None):
        return self.request("PUT", endpoint, data=data, headers=headers)

    def spatch(self, endpoint, data, headers=None):
        return self.request("PATCH", endpoint, data=data, headers=headers)

    def sget(self, endpoint, params=None, headers=None):
        return self.request("GET", endpoint, params=params, headers=headers)

    def shead(self, endpoint, headers=None):
        return self.request("HEAD", endpoint, headers=headers)
