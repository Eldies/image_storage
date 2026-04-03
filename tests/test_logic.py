# -*- coding: utf-8 -*-
import random
from typing import Any, Generator
from unittest.mock import Mock, patch

import pytest

from app.logic import randomize_filename


@pytest.fixture()
def time_mock() -> Generator[Mock, Any, None]:
    mock = Mock(return_value=1657234419.0)
    with patch("time.time", mock):
        yield mock


class TestGenerateImageUUID:
    @pytest.fixture(autouse=True)
    def _setup(self, time_mock):
        self.time_mock = time_mock
        random.seed(0)

    def test_with_name(self):
        assert randomize_filename("FOO") == "FOO-qkRkXu8ab9"

    def test_without_name(self):
        assert randomize_filename() == "qkRkXu8ab9"

    def test_empty_string(self):
        assert randomize_filename("") == "qkRkXu8ab9"

    def test_changes_with_millisecond(self):
        assert randomize_filename() == "qkRkXu8ab9"
        self.time_mock.return_value += 0.001
        random.seed(0)
        assert randomize_filename() == "qkRkXu8abA"
        # checking that it does not change just because of calling this function again
        random.seed(0)
        assert randomize_filename() == "qkRkXu8abA"

    def test_changes_with_random(self):
        assert randomize_filename() == "qkRkXu8ab9"
        random.seed(1)
        assert randomize_filename() == "8rmkXu8ab9"
        # checking that it does not change just because of calling this function again
        random.seed(1)
        assert randomize_filename() == "8rmkXu8ab9"
