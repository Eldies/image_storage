# -*- coding: utf-8 -*-
import json
import logging
from functools import cached_property
import uuid

from flask import (
    abort,
    jsonify,
    make_response,
    request,
)
from flask.views import MethodView

from auth import (
    get_user_id_from_token,
    InvalidTokenError,
)
from storage_manager import StorageManager


def ping():
    return 'pong'


TOKEN_PREFIX = 'Bearer '


class ImageView(MethodView):
    def abort(self, status_code, error):
        abort(make_response(jsonify(error=error), status_code))

    @cached_property
    def user_id(self):
        token = request.headers.get('Authorization')
        logging.debug('Provided token: "{}"'.format(token))
        if token is None:
            self.abort(401, error='Token not provided')
        if not token.startswith(TOKEN_PREFIX):
            self.abort(403, error='Invalid token')

        token = token[len(TOKEN_PREFIX):].strip()

        try:
            return get_user_id_from_token(token)
        except InvalidTokenError:
            self.abort(403, error='Invalid token')

    @cached_property
    def storage_manager(self):
        return StorageManager()

    def generate_new_uuid(self):
        generated = str(uuid.uuid4())
        while self.storage_manager.uuid_exists(generated):
            logging.debug('Uuid "{}" already exists. Regenerating'.format(generated))
            generated = str(uuid.uuid4())
        logging.debug('Generated uuid "{}"'.format(generated))
        return generated

    def post(self):
        data = dict(
            dict(request.form),
            owner=self.user_id,
        )

        if 'file' not in request.files:
            self.abort(400, error='No file')

        uuid = self.generate_new_uuid()

        self.storage_manager.save_image(
            uuid,
            request.files.get('file'),
            json.dumps(data),
        )
        return jsonify(dict(
            status='ok',
            uuid=uuid,
        ))
