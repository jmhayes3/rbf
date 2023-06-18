import os


class Config(object):
    TESTING = False
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENGINE_URI = os.environ.get("MESSENGER_URI")


class TestConfig(Config):
    TESTING = True