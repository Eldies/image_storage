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
    check_api_key,
    InvalidApiKey,
)
from storage_manager import StorageManager


def ping():
    return 'pong'


class ImageView(MethodView):
    def abort(self, status_code, error):
        abort(make_response(jsonify(error=error), status_code))

    def check_auth(self):
        api_key = request.headers.get('X-API-KEY')
        logging.debug('Provided api_key: "{}"'.format(api_key))
        if api_key is None:
            self.abort(401, 'Unauthorized')

        try:
            check_api_key(api_key)
        except InvalidApiKey:
            self.abort(403, error='Invalid api key')

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
        self.check_auth()

        if 'file' not in request.files:
            self.abort(400, error='No file')

        file = request.files.get('file')

        data = dict(
            data=dict(request.form),
            mimetype=file.mimetype,
        )
        uuid = self.generate_new_uuid()

        self.storage_manager.save_image(
            uuid,
            file,
            json.dumps(data),
        )
        return jsonify(dict(
            status='ok',
            uuid=uuid,
        ))
