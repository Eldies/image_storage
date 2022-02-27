# -*- coding: utf-8 -*-
from flask import Flask
from logging.config import dictConfig

import settings
import views


def create_app():

    app = Flask(__name__)

    app.add_url_rule('/ping', view_func=views.ping)

    app.add_url_rule('/v1/image/', view_func=views.ImageView.as_view('image_post'), methods=['POST'])
    app.add_url_rule('/v1/image/<filename>', view_func=views.ImageView.as_view('image_post2'), methods=['POST'])
    app.add_url_rule('/v1/image/<uuid>', view_func=views.ImageView.as_view('image_get'), methods=['GET'])

    dictConfig(settings.LOGGING_CONFIG)

    return app


app = create_app()
