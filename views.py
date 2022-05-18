# -*- coding: utf-8 -*-
import base64
from itertools import chain
import json
import logging
from functools import cached_property
import uuid
from io import BytesIO

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

    def generate_filename(self):
        suggested_filename = self.form_values.get('filename') or self.form_values.get('file_name')
        return '{}-{}'.format(
            suggested_filename or base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")[:5],
            base64.urlsafe_b64encode(uuid.uuid1().bytes).decode("utf-8")[:-2],
        )

    def _process_file(self):
        file = request.files.get('file')

        stream = BytesIO()
        file.save(stream)
        stream.seek(0)
        file_content = stream.read()

        if len(file_content) == 0:
            self.abort(400, error='Empty file')

        return file_content, file.mimetype

    def _process_base64(self):
        encoded = self.form_values['base64']
        file_content = base64.b64decode(encoded)

        del self.form_values['base64']

        return file_content, 'image/jpeg'

    @cached_property
    def form_values(self):
        return {
            key.lower(): value
            for key, value in chain(
                request.form.items(),
                request.json.items() if request.is_json else [],
            )
        }

    def post(self):
        self.check_auth()

        if 'file' in request.files:
            file_content, mimetype = self._process_file()
        elif self.form_values.get('base64'):
            file_content, mimetype = self._process_base64()
        else:
            self.abort(400, error='No file')

        filename = self.generate_filename()
        logging.debug('Saving with uuid: {}'.format(filename))

        data = dict(
            data=self.form_values,
            mimetype=mimetype,
            content_length=len(file_content),
        )

        self.storage_manager.save_image(
            filename,
            file_content,
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
