import os


class Config(object):
    TESTING = False
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENGINE_URI = "tcp://127.0.0.1:5557"


class TestConfig(Config):
    TESTING = True