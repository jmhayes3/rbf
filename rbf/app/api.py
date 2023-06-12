import json

from werkzeug.exceptions import abort

from flask import (
    Blueprint, redirect, request, url_for, jsonify
)
from flask_login import login_required, current_user

from app import db
from app.models import User, Module

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/modules/", methods=("GET",))
@login_required
def get_modules():
    pass


@bp.route("/module/<int:id>", methods=("GET",))
@login_required
def get_module():
    pass


@bp.route("/module/<int:id>/triggered", methods=("GET",))
@login_required
def get_module_triggered_items():
    pass
