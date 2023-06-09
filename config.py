import os


class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "options": "-c timezone=utc"
            }
    }
    ENGINE_URI = os.environ.get("MESSENGER_URI")
