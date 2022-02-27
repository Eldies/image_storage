# -*- coding: utf-8 -*-
import os


UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.curdir), 'uploads')

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
        'level': 'INFO',
        'handlers': ['console']
    },
}