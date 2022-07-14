# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class ClientInfo:
    id: str
    api_key: str
