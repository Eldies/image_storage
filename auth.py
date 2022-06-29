# -*- coding: utf-8 -*-
import settings


class InvalidApiKey(ValueError):
    pass


def check_api_key(api_key: str) -> None:
    if api_key != settings.CLIENT_API_KEY:
        raise InvalidApiKey()
