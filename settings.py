# -*- coding: utf-8 -*-
import os


UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

CLIENT_API_KEY = os.environ.get('CLIENT_API_KEY')

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
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