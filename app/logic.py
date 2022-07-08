# -*- coding: utf-8 -*-
import base58
import time
import uuid

from .types import ClientInfo
from . import settings


def get_client_info_by_api_key(api_key: str) -> ClientInfo | None:
    for client in settings.CLIENTS_INFO:
        if api_key == client.api_key:
            return client


def generate_image_uuid(suggested_filename: str | None) -> str:
    """
    Generates uuid, tries to make it unique:
        uses timestamp in milliseconds, so uuids generated in different milliseconds should differ
        for uuids generated at the same millisecond, adds 5 random base58 symbols, which gives 58^3=195112 options
    """
    random_string = base58.b58encode(uuid.uuid4().bytes).decode("utf-8")[:3]
    timestamp_ms = int(time.time() * 1000)
    unique_part = '{}{}'.format(random_string, base58.b58encode_int(timestamp_ms).decode("utf-8"))
    if suggested_filename:
        return '{}-{}'.format(suggested_filename, unique_part)
    else:
        return unique_part
