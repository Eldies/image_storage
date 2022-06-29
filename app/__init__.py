# -*- coding: utf-8 -*-
from flask import Flask
from logging.config import dictConfig

from . import (
    settings,
    views,
)


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__)

    if test_config is not None:
        app.config.update(test_config)

    app.add_url_rule('/ping', view_func=views.ping)

    app.add_url_rule('/v1/image/', view_func=views.ImageView.as_view('image_post'), methods=['POST'])
    app.add_url_rule('/v1/image/<uuid>', view_func=views.ImageView.as_view('image_get'), methods=['GET'])

    dictConfig(settings.LOGGING_CONFIG)

    return app
