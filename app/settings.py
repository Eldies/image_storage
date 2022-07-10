# -*- coding: utf-8 -*-
import os

from .types import ClientInfo


UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

CLIENTS_INFO = [
    ClientInfo(id=os.environ[env_var].split(':')[0], api_key=os.environ[env_var].split(':')[1])
    for env_var in os.environ
    if 'CLIENT_CREDENTIALS_' in env_var
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
