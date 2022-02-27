# -*- coding: utf-8 -*-
from flask import Flask
from logging.config import dictConfig

import settings
import views


def create_app():

    app = Flask(__name__)

    app.add_url_rule('/ping', view_func=views.ping)

    dictConfig(settings.LOGGING_CONFIG)

    return app

app = create_app()
