# -*- coding: utf-8 -*-
import tempfile

import pytest


@pytest.fixture()
def upload_folder(monkeypatch) -> str:
    return tempfile.mkdtemp()
