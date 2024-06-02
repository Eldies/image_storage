# -*- coding: utf-8 -*-
import random
import time

import base58

from .settings import get_settings
from .schemas import ClientInfo


def get_client_info_by_api_key(api_key: str) -> ClientInfo | None:
    for client in get_settings().clients_info.values():
        if api_key == client.api_key:
            return client
    return None


def generate_image_uuid(suggested_filename: str | None) -> str:
    """
    Generates uuid, tries to make it unique:
        uses timestamp in milliseconds, so uuids generated in different milliseconds should differ
        for uuids generated at the same millisecond, adds 3 random base58 symbols, which gives 58^3=195112 options
    """
    random_string = "".join(random.choice(base58.alphabet.decode()) for _ in range(3))
    timestamp_ms = int(time.time() * 1000)
    unique_part = "{}{}".format(random_string, base58.b58encode_int(timestamp_ms).decode("utf-8"))
    if suggested_filename:
        return "{}-{}".format(suggested_filename, unique_part)
    else:
        return unique_part
