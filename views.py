# -*- coding: utf-8 -*-
import base64
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

    def generate_filename(self, suggested_filename):
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

        data = dict(
            data=dict(request.form),
            mimetype=file.mimetype,
            content_length=len(file_content),
        )

        return file_content, data

    def _process_base64(self, form_data):
        encoded = form_data['base64']
        file_content = base64.b64decode(encoded)

        del form_data['base64']

        data = dict(
            data=form_data,
            mimetype='image/jpeg',
            content_length=len(file_content),
        )

        return file_content, data

    def get_filename_from_form(self):
        for key in request.form:
            if key.lower() in ['filename', 'file_name']:
                return request.form[key]
        try:
            for key in request.json:
                if key.lower() in ['filename', 'file_name']:
                    return request.json[key]
        except:
            pass

    def post(self):
        self.check_auth()

        if 'file' in request.files:
            file_content, data = self._process_file()
        elif request.form.get('base64'):
            file_content, data = self._process_base64(dict(request.form))
        elif request.is_json and request.json.get('base64'):
            file_content, data = self._process_base64(request.json)
        else:
            self.abort(400, error='No file')

        filename = self.generate_filename(self.get_filename_from_form())
        logging.debug('Saving with uuid: {}'.format(filename))

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
