# -*- coding: utf-8 -*-
import os
from parameterized import parameterized
import unittest
from unittest.mock import patch, mock_open, Mock

import settings
from storage_manager import StorageManager


class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.manager = StorageManager()

        self.open_mock = mock_open()
        self.makedirs_mock = Mock()
        self.file_mock = Mock()
        self.exists_mock = Mock()

        self.patches = [
            patch("builtins.open", self.open_mock),
            patch("storage_manager.os.makedirs", self.makedirs_mock),
            patch("storage_manager.os.path.exists", self.exists_mock),
            patch('settings.UPLOAD_FOLDER', 'some_path'),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def check_save(self, uuid, data=None):
        folder = os.path.join(settings.UPLOAD_FOLDER, uuid)
        file_path = os.path.join(folder, 'file')
        data_path = os.path.join(folder, 'data')

        assert self.makedirs_mock.call_count == 1
        assert self.makedirs_mock.call_args.args == (folder,)

        assert self.file_mock.save.call_count == 1
        assert self.file_mock.save.call_args.args == (file_path,)

        assert self.open_mock.call_count == (1 if data else 0)
        if data:
            assert self.open_mock.call_args.args == (data_path, 'w')
            assert self.open_mock.return_value.__enter__.return_value.write.call_count == 1
            assert self.open_mock.return_value.__enter__.return_value.write.call_args.args == (data,)

    def test_save_image_ok(self):
        self.manager.save_image('some_uuid', self.file_mock, 'some_data')
        self.check_save('some_uuid', 'some_data')

    def test_save_image_no_data_ok(self):
        self.manager.save_image('some_uuid', self.file_mock)
        self.check_save('some_uuid')

    @parameterized.expand([(True,), (False,)])
    def test_exists(self, exists):
        self.exists_mock.return_value = exists
        assert self.manager.uuid_exists('some_uuid') == exists
        assert self.exists_mock.call_count == 1
        assert self.exists_mock.call_args.args == (os.path.join(settings.UPLOAD_FOLDER, 'some_uuid'), )
