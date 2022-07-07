# -*- coding: utf-8 -*-
import base64
import uuid

from .types import ClientInfo
from . import settings


def get_client_info_by_api_key(api_key: str) -> ClientInfo | None:
    for client in settings.CLIENTS_INFO:
        if api_key == client.api_key:
            return client


def generate_image_uuid(suggested_filename: str) -> str:
    return '{}-{}'.format(
        suggested_filename or base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")[:5],
        base64.urlsafe_b64encode(uuid.uuid1().bytes).decode("utf-8")[:-2],
    )
