"""Web application frontend."""

from flask import Flask

from .config import Config


def create_app(config_object=Config):
    """Application factory function for Flask app."""

    app = Flask(__name__)
    app.config.from_object(config_object)

    from .models import db
    db.init_app(app)

    with app.app_context():
        from .models import AppUser
        db.create_all()

    from .auth import login_manager

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .auth import auth_bp
    from .main import main_bp
    from .api import api_bp
    from .module import module_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(module_bp)

    from .filters import format_datetime, format_timestamp

    app.jinja_env.filters["format_datetime"] = format_datetime
    app.jinja_env.filters["format_timestamp"] = format_timestamp

    return app
