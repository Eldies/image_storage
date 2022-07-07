# -*- coding: utf-8 -*-
import base64
from itertools import chain
import json
import logging
from functools import cached_property
from io import BytesIO

from flask import (
    abort,
    jsonify,
    request,
    Response,
    send_file,
)
from flask.views import MethodView

from .logic import (
    get_client_info_by_api_key,
    generate_image_uuid,
)
from .storage_manager import StorageManager
from .types import ClientInfo


def ping():
    return 'pong'


class ImageView(MethodView):
    def get_client(self) -> ClientInfo:
        api_key = request.headers.get('X-API-KEY')
        logging.debug('Provided api_key: "{}"'.format(api_key))
        if api_key is not None:
            return get_client_info_by_api_key(api_key)

    def check_auth(self):
        if self.get_client() is None:
            abort(401, 'Unauthorized')

    @cached_property
    def storage_manager(self) -> StorageManager:
        return StorageManager()

    def _process_file(self):
        file = request.files.get('file')

        stream = BytesIO()
        file.save(stream)
        stream.seek(0)
        file_content = stream.read()

        if len(file_content) == 0:
            abort(400, 'Empty file')

        return file_content, file.mimetype

    def _process_base64(self):
        encoded = self.form_values['base64']
        file_content = base64.b64decode(encoded)

        del self.form_values['base64']

        return file_content, 'image/jpeg'

    @cached_property
    def form_values(self) -> dict:
        return {
            key.lower(): value
            for key, value in chain(
                request.form.items(),
                request.json.items() if request.is_json else [],
            )
        }

    def post(self) -> Response:
        self.check_auth()

        if 'file' in request.files:
            file_content, mimetype = self._process_file()
        elif self.form_values.get('base64'):
            file_content, mimetype = self._process_base64()
        else:
            abort(400, 'No file')

        filename = generate_image_uuid(self.form_values.get('filename') or self.form_values.get('file_name'))
        logging.debug('Saving with uuid: {}'.format(filename))

        data = dict(
            data=self.form_values,
            mimetype=mimetype,
            content_length=len(file_content),
        )

        self.storage_manager.save_image(
            [filename],
            file_content,
            json.dumps(data),
        )
        return jsonify(dict(
            status='ok',
            uuid=filename,
        ))

    def get(self, uuid: str, client_id: str = None) -> Response:
        uuid = ([client_id] if client_id else []) + [uuid]
        if not self.storage_manager.uuid_exists(uuid):
            abort(404, 'Not Found')
        return send_file(
            self.storage_manager.read_file(uuid),
            mimetype=json.loads(self.storage_manager.read_data(uuid)).get('mimetype'),
        )
