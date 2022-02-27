# -*- coding: utf-8 -*-
import base64
import json
import logging
from functools import cached_property
import uuid

from flask import (
    abort,
    jsonify,
    make_response,
    request,
    send_file,
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
        abort(make_response(
            jsonify(
                error=error,
                status='error',
            ),
            status_code,
        ))

    def check_auth(self):
        logging.debug('All headers: {}'.format(request.headers))
        logging.debug('All header keys: {}'.format(list(request.headers.keys())))
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

    def generate_random_filename(self):
        return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")[:5]

    def generate_time_based_suffix(self):
        return base64.urlsafe_b64encode(uuid.uuid1().bytes).decode("utf-8")[:-2]

    def post(self, filename=None):
        self.check_auth()

        if 'file' not in request.files:
            self.abort(400, error='No file')

        file = request.files.get('file')

        data = dict(
            data=dict(request.form),
            mimetype=file.mimetype,
            original_filename=file.filename,
            given_filename=filename,
        )

        if filename is None:
            filename = self.generate_random_filename()

        filename += '-' + self.generate_time_based_suffix()

        self.storage_manager.save_image(
            filename,
            file,
            json.dumps(data),
        )
        return jsonify(dict(
            status='ok',
            uuid=filename,
        ))

    def get(self, uuid):
        if not self.storage_manager.uuid_exists(uuid):
            self.abort(404, 'Not Found')
        return send_file(
            self.storage_manager.read_file(uuid),
            mimetype=json.loads(self.storage_manager.read_data(uuid)).get('mimetype'),
        )
