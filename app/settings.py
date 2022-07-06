# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass


@dataclass
class ClientInfo:
    id: str
    api_key: str


UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

CLIENTS_INFO = [
    ClientInfo(id='toysdb', api_key=os.environ.get('CLIENT_API_KEY')),
]

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    },
}
