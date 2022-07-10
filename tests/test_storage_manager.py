# -*- coding: utf-8 -*-
import os

import pytest
from unittest.mock import (
    Mock,
    mock_open,
    patch,
)

from app.storage_manager import StorageManager


class TestStorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        self.manager = StorageManager()

        self.open_mock = mock_open()
        self.makedirs_mock = Mock()
        self.exists_mock = Mock()

        self.patches = [
            patch("builtins.open", self.open_mock),
            patch("os.makedirs", self.makedirs_mock),
            patch("os.path.exists", self.exists_mock),
        ]
        for p in self.patches:
            p.start()

        yield

        for p in self.patches:
            p.stop()

    def check_save(self, uuid, data=None):
        folder = os.path.join('test_upload_path', uuid)
        file_path = os.path.join(folder, 'file')
        data_path = os.path.join(folder, 'data')

        assert self.makedirs_mock.call_count == 1
        assert self.makedirs_mock.call_args.args == (folder,)

        assert self.open_mock.call_count == (2 if data else 1)
        assert self.open_mock.return_value.__enter__.return_value.write.call_count == (2 if data else 1)
        assert self.open_mock.call_args_list[0].args == (file_path, 'wb')
        assert self.open_mock.return_value.__enter__.return_value.write.call_args_list[0].args == (b'abcdef',)
        if data:
            assert self.open_mock.call_args_list[1].args == (data_path, 'w')
            assert self.open_mock.return_value.__enter__.return_value.write.call_args_list[1].args == (data,)

    def test_save_image_ok(self):
        self.manager.save_image(['some_uuid'], b'abcdef', 'some_data')
        self.check_save('some_uuid', 'some_data')

    def test_save_image_no_data_ok(self):
        self.manager.save_image(['some_uuid'], b'abcdef')
        self.check_save('some_uuid')

    @pytest.mark.parametrize('exists', [True, False])
    def test_exists(self, exists):
        self.exists_mock.return_value = exists
        assert self.manager.uuid_exists(['some_uuid']) == exists
        assert self.exists_mock.call_count == 1
        assert self.exists_mock.call_args.args == (os.path.join('test_upload_path', 'some_uuid'),)

    def test_read_data(self):
        self.open_mock.return_value.__enter__.return_value.read.return_value = 'READ DATA'

        assert self.manager.read_data(['some_uuid']) == 'READ DATA'

        folder = os.path.join('test_upload_path', 'some_uuid')
        data_path = os.path.join(folder, 'data')

        assert self.open_mock.call_args.args == (data_path, 'r')

    def test_read_file(self):
        self.manager.read_file(['some_uuid'])

        folder = os.path.join('test_upload_path', 'some_uuid')
        file_path = os.path.join(folder, 'file')
        assert self.open_mock.call_args.args == (file_path, 'rb')

    def test_path_for_uuid(self):
        assert self.manager.path_for_uuid(['foo']) == 'test_upload_path{}foo'.format(os.sep)

    def test_path_for_uuid_with_sep(self):
        path = self.manager.path_for_uuid(['foo', 'bar'])
        assert path == 'test_upload_path{sep}foo{sep}bar'.format(sep=os.sep)
