import os

class Config(object):
    TESTING = False
    SECRET_KEY = "dev"
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/foo.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "options": "-c timezone=utc"
            }
    }
    ENGINE_URI = os.environ.get("MESSENGER_URI")
