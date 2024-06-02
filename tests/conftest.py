# -*- coding: utf-8 -*-
import tempfile

import pytest


@pytest.fixture()
def upload_folder() -> str:
    return tempfile.mkdtemp()
