# -*- coding: utf-8 -*-
import base64
import json
import logging
from functools import cached_property

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
from .schemas import ClientInfo


def ping():
    return 'pong'


class ImageView(MethodView):
    @cached_property
    def client(self) -> ClientInfo:
        api_key = request.headers.get('X-API-KEY')
        logging.debug('Provided api_key: "{}"'.format(api_key))
        if api_key is not None:
            return get_client_info_by_api_key(api_key)

    def check_auth(self):
        if self.client is None:
            abort(401, 'Unauthorized')

    @cached_property
    def storage_manager(self) -> StorageManager:
        return StorageManager()

    def post(self) -> Response:
        self.check_auth()

        if not request.json.get('base64'):
            abort(400, 'No file')

        filename = generate_image_uuid(request.json.get('file_name'))
        logging.debug('Saving image with uuid "{}" for client "{}"'.format(filename, self.client.id))

        self.storage_manager.save_image(
            uuid=[self.client.id, filename],
            file_content=base64.b64decode(request.json['base64']),
            data=json.dumps(dict(
                mimetype='image/jpeg',
            )),
        )
        return jsonify(dict(
            status='ok',
            uuid='{}/{}'.format(self.client.id, filename),
        ))

    def get(self, uuid: str, client_id: str) -> Response:
        uuid = [client_id, uuid]
        if not self.storage_manager.uuid_exists(uuid):
            abort(404, 'Not Found')
        return send_file(
            self.storage_manager.read_file(uuid),
            mimetype=json.loads(self.storage_manager.read_data(uuid)).get('mimetype'),
        )
