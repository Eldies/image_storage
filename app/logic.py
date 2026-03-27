# -*- coding: utf-8 -*-
import random
import time

import base58

from .settings import ClientInfo, settings


def get_client_info_by_api_key(api_key: str) -> ClientInfo | None:
    for client in settings.clients_info.values():
        if api_key == client.api_key:
            return client
    return None


def randomize_filename(suggested_filename: str | None = None) -> str:
    """
    Generates uuid, tries to make it unique:
        uses timestamp in milliseconds, so uuids generated in different milliseconds should differ
        for uuids generated at the same millisecond, adds 3 random base58 symbols, which gives 58^3=195112 options
    """
    random_string = "".join(random.choices(base58.alphabet.decode(), k=3))
    timestamp_string = base58.b58encode_int(int(time.time() * 1000)).decode("utf-8")
    result = f"{random_string}{timestamp_string}"
    if suggested_filename:
        result = f"{suggested_filename}-{result}"
    return result


def generate_uuid(suggested_filename: str | None, client: ClientInfo) -> list[str]:
    return [client.id, randomize_filename(suggested_filename)]
