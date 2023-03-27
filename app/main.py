from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

bp = Blueprint("main", __name__)


@bp.route("/", methods=("GET",))
@bp.route("/index", methods=("GET",))
def index():
    return redirect(url_for("module.index"))