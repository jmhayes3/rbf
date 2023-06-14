import pytest

from rbf.web import create_app
from rbf.web.config import TestConfig


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app(config_object=TestConfig)
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client
