# -*- coding: utf-8 -*-
import random
import time

import base58

from app.settings import ClientInfo


def randomize_filename(suggested_filename: str | None = None) -> str:
    random_string = "".join(random.choices(base58.alphabet.decode(), k=3))
    timestamp_string = base58.b58encode_int(int(time.time() * 1000)).decode("utf-8")
    result = f"{random_string}{timestamp_string}"
    if suggested_filename:
        result = f"{suggested_filename}-{result}"
    return result


def generate_uuid(suggested_filename: str | None, client: ClientInfo) -> list[str]:
    return [client.id, randomize_filename(suggested_filename)]
