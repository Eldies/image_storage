# -*- coding: utf-8 -*-
from .types import ClientInfo
from . import settings


def get_client_info_by_api_key(api_key: str) -> ClientInfo | None:
    for client in settings.CLIENTS_INFO:
        if api_key == client.api_key:
            return client
