# -*- coding: utf-8 -*-
import base64
import json
import logging

from flask import (
    jsonify,
    request,
    Response,
    send_file,
)
from werkzeug.exceptions import (
    BadRequest,
    NotFound,
    Unauthorized,
)

from .logic import (
    get_client_info_by_api_key,
    generate_image_uuid,
)
from .storage_manager import (
    get_storage_manager,
    StorageManagerException,
)


def ping():
    return 'pong'


def post_image() -> Response:
    api_key = request.headers.get('X-API-KEY')
    logging.debug('Provided api_key: "{}"'.format(api_key))
    client = None
    if api_key is not None:
        client = get_client_info_by_api_key(api_key)

    if client is None:
        raise Unauthorized()

    if not request.json.get('base64'):
        raise BadRequest('No file')

    filename = generate_image_uuid(request.json.get('file_name'))
    logging.debug('Saving image with uuid "{}" for client "{}"'.format(filename, client.id))

    get_storage_manager().save_image(
        uuid=[client.id, filename],
        file_content=base64.b64decode(request.json['base64']),
        data=json.dumps(dict(
            mimetype='image/jpeg',
        )),
    )
    return jsonify(dict(
        status='ok',
        uuid='{}/{}'.format(client.id, filename),
    ))


def get_image(uuid: str, client_id: str) -> Response:
    try:
        file, data = get_storage_manager().get_file([client_id, uuid])
        return send_file(file, mimetype=data.get('mimetype'))
    except StorageManagerException as e:
        raise NotFound(*e.args)
