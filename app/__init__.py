# -*- coding: utf-8 -*-
from flask import (
    Flask,
    jsonify,
    Response,
)
from logging.config import dictConfig

from werkzeug.exceptions import HTTPException

from . import (
    settings,
    views,
)


def error_handler(error: HTTPException) -> (Response, int):
    return jsonify(dict(status='error', error=error.description)), error.code


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__)

    if test_config is not None:
        app.config.update(test_config)

    app.add_url_rule('/ping', view_func=views.ping)

    app.add_url_rule('/v1/image/', view_func=views.ImageView.as_view('image_post'), methods=['POST'])
    app.add_url_rule('/v1/image/<client_id>/<uuid>', view_func=views.ImageView.as_view('image_get2'), methods=['GET'])

    app.register_error_handler(400, error_handler)
    app.register_error_handler(401, error_handler)
    app.register_error_handler(404, error_handler)

    dictConfig(settings.LOGGING_CONFIG)

    return app
