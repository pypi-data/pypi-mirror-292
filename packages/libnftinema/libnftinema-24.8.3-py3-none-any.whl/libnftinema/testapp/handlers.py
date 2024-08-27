from typing import Optional

from django.conf import settings

from libnftinema.common import get_client_key
from libnftinema.structs import ClientKey


def check_api_client_test(client_id: str) -> (bool, Optional[ClientKey]):

    if client_id == "api_client_AoYznPzrHMMv4oR2vFjSQC":
        return True, get_client_key()
    return False, None
