# -*- coding: utf-8 -*-
import os

import settings


class StorageManager(object):
    def uuid_exists(self, uuid):
        filepath = os.path.join(settings.UPLOAD_FOLDER, uuid)
        return os.path.exists(filepath)

    def save_image(self, uuid, file, data=None):
        folder = os.path.join(settings.UPLOAD_FOLDER, uuid)
        os.makedirs(folder)
        file.save(os.path.join(folder, 'file'))
        if data:
            with open(os.path.join(folder, 'data'), 'w') as f:
                f.write(data)
