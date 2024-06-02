# -*- coding: utf-8 -*-
import tempfile

import pytest

from app import settings


@pytest.fixture()
def upload_folder(monkeypatch) -> str:
    folder = tempfile.mkdtemp()
    monkeypatch.setenv("UPLOAD_FOLDER", folder)
    return folder


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    monkeypatch.setattr(settings, "_settings", None)
