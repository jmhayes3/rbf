import os

import pytest

import praw

from rbf.web import create_app
from rbf.web.config import TestConfig


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app(config_object=TestConfig)
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


@pytest.fixture(scope="module")
def praw_session():
    session = praw.Reddit(
        user_agent=os.environ.get("APP_USER_AGENT"),
        client_id=os.environ.get("APP_KEY"),
        client_secret=os.environ.get("APP_SECRET"),
        password=os.environ.get("APP_PASSWORD"),
        username=os.environ.get("APP_USERNAME"),
    )
    return session