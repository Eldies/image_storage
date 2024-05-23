# -*- coding: utf-8 -*-
import os

from .schemas import ClientInfo


UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")

CLIENTS_INFO = [
    ClientInfo(id=os.environ[env_var].split(":")[0], api_key=os.environ[env_var].split(":")[1])
    for env_var in os.environ
    if "CLIENT_CREDENTIALS_" in env_var
]
