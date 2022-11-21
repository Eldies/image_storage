# -*- coding: utf-8 -*-
import os

import pytest

from app.storage_manager import StorageManager


class TestStorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, settings, fs):
        self.fake_filesystem = fs

    def check_save(self, uuid, data=None):
        folder = os.path.join('/test_upload_path', uuid)
        file_path = os.path.join(folder, 'file')
        data_path = os.path.join(folder, 'data')

        assert self.fake_filesystem.isdir(folder)
        assert self.fake_filesystem.isfile(file_path)
        with open(file_path, 'rb') as file:
            assert file.read() == b'abcdef'
        if data is not None:
            assert self.fake_filesystem.isfile(data_path)
            with open(data_path, 'r') as file:
                assert file.read() == data

    def test_save_image_ok(self):
        StorageManager().save_image(['some_uuid'], b'abcdef', 'some_data')
        self.check_save('some_uuid', 'some_data')

    def test_save_image_no_data_ok(self):
        StorageManager().save_image(['some_uuid'], b'abcdef')
        self.check_save('some_uuid')

    @pytest.mark.parametrize('exists', [True, False])
    def test_exists(self, exists):
        if exists:
            self.fake_filesystem.create_file('/test_upload_path/some_uuid')
        assert StorageManager().uuid_exists(['some_uuid']) == exists

    def test_read_data(self):
        self.fake_filesystem.create_file('/test_upload_path/some_uuid/data', contents='READ DATA')
        assert StorageManager().read_data(['some_uuid']) == 'READ DATA'

    def test_read_file(self):
        self.fake_filesystem.create_file('/test_upload_path/some_uuid/file', contents=b'READ DATA')
        assert StorageManager().read_file(['some_uuid']).read() == b'READ DATA'

    def test_path_for_uuid(self):
        assert StorageManager().path_for_uuid(['foo']) == '/test_upload_path{}foo'.format(os.sep)

    def test_path_for_uuid_with_sep(self):
        path = StorageManager().path_for_uuid(['foo', 'bar'])
        assert path == '/test_upload_path{sep}foo{sep}bar'.format(sep=os.sep)
