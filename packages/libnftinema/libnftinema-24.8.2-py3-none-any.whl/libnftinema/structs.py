import json
from dataclasses import dataclass

import jwt


@dataclass
class ClientKey:
    raw: str
    parsed: dict = None
    kid: str = None
    jwk: str = None
    k: bytes = None

    def __post_init__(self):
        key = jwt.decode(self.raw, None, options={"verify_signature": False})
        self.parsed = key
        self.kid = key["kid"]
        self.jwk = json.dumps(key)
        self.k = jwt.algorithms.get_default_algorithms()["HS256"].from_jwk(key)
