# -*- coding: utf-8 -*-
import os


class StorageManager(object):
    def __init__(self):
        self.dir = os.path.join(os.path.abspath(os.path.curdir), 'uploads')

    def uuid_exists(self, uuid):
        filepath = os.path.join(self.dir, uuid)
        return os.path.exists(filepath)

    def save_image(self, uuid, file, data=None):
        folder = os.path.join(self.dir, uuid)
        os.makedirs(folder)
        file.save(os.path.join(folder, 'file'))
        if data:
            with open(os.path.join(folder, 'data')) as f:
                f.write(data)
