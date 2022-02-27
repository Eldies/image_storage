# -*- coding: utf-8 -*-
import os

import settings


class StorageManager(object):
    def path_for_uuid(self, uuid):
        return os.path.join(settings.UPLOAD_FOLDER, uuid)

    def uuid_exists(self, uuid):
        return os.path.exists(self.path_for_uuid(uuid))

    def save_image(self, uuid, file_content, data=None):
        folder = self.path_for_uuid(uuid)
        os.makedirs(folder)
        with open(os.path.join(folder, 'file'), 'wb') as f:
            f.write(file_content)
        if data:
            with open(os.path.join(folder, 'data'), 'w') as f:
                f.write(data)

    def read_data(self, uuid):
        with open(os.path.join(self.path_for_uuid(uuid), 'data'), 'r') as f:
            return f.read()

    def read_file(self, uuid):
        return open(os.path.join(self.path_for_uuid(uuid), 'file'), 'rb')
