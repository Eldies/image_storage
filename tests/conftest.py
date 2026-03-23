# -*- coding: utf-8 -*-
import boto3
import pytest
from moto import mock_aws

from app.settings import Settings


@pytest.fixture(scope="session", autouse=True)
def mock_s3_bucket():
    with mock_aws():
        conn = boto3.resource("s3")
        yield conn.create_bucket(Bucket="mybucket")


@pytest.fixture(autouse=True)
def clean_s3_bucket(mock_s3_bucket):
    mock_s3_bucket.objects.delete()


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, mock_s3_bucket):
    settings = Settings.model_construct()
    monkeypatch.setattr("app.settings.get_settings", lambda: settings)
    yield settings
