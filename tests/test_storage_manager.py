# -*- coding: utf-8 -*-
import os

import pytest

from app.storage_manager import StorageManager


@pytest.mark.asyncio
class TestStorageManager:
    @pytest.fixture(autouse=True)
    def _setup(self, settings, upload_folder):
        self.upload_folder = upload_folder

    def check_save(self, uuid, data=None):
        folder = os.path.join(self.upload_folder, uuid)
        file_path = os.path.join(folder, 'file')
        data_path = os.path.join(folder, 'data')

        assert os.path.isdir(folder)
        assert os.path.isfile(file_path)
        with open(file_path, 'rb') as file:
            assert file.read() == b'abcdef'
        if data is not None:
            assert os.path.isfile(data_path)
            with open(data_path, 'r') as file:
                assert file.read() == data

    async def test_save_image_ok(self):
        await StorageManager().save_image(['some_uuid'], b'abcdef', 'some_data')
        self.check_save('some_uuid', 'some_data')

    async def test_save_image_no_data_ok(self):
        await StorageManager().save_image(['some_uuid'], b'abcdef')
        self.check_save('some_uuid')

    @pytest.mark.parametrize('exists', [True, False])
    def test_exists(self, exists):
        if exists:
            os.makedirs(os.path.join(self.upload_folder, 'some_uuid'))
        assert StorageManager().uuid_exists(['some_uuid']) == exists

    async def test_read_data(self):
        os.makedirs(os.path.join(self.upload_folder, 'some_uuid'))
        with open(os.path.join(self.upload_folder, 'some_uuid', 'data'), 'w') as f:
            f.write('{"foo": "bar"}')
        assert await StorageManager()._read_data(['some_uuid']) == {"foo": "bar"}

    async def test_read_file(self):
        os.makedirs(os.path.join(self.upload_folder, 'some_uuid'))
        with open(os.path.join(self.upload_folder, 'some_uuid', 'file'), 'wb') as f:
            f.write(b'READ DATA')
        assert await StorageManager()._read_file(['some_uuid']) == b'READ DATA'

    def test_path_for_uuid_with_sep(self):
        path = StorageManager().path_for_uuid(['foo', 'bar'])
        assert path == os.path.join(self.upload_folder, 'foo', 'bar')
