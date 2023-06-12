import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from rbf.config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login.init_app(app)

    from . import auth, main, api, module, cli

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(module.bp)
    app.register_blueprint(cli.bp)
    
    from . import filters

    app.jinja_env.filters["format_datetime"] = filters.format_datetime
    app.jinja_env.filters["format_timestamp"] = filters.format_timestamp

    return app
