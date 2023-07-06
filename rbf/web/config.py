import os

from dotenv import load_dotenv


load_dotenv()


class Config(object):
    TESTING = False
    DEBUG = True
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENGINE_URI = os.environ.get("ENGINE_URI")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENGINE_URI = os.environ.get("ENGINE_URI")