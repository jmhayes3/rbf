from flask import (
    Blueprint, redirect, url_for
)


main_bp = Blueprint("main", __name__, url_prefix="/")


@main_bp.route("/", methods=("GET",))
@main_bp.route("/index", methods=("GET",))
def index():
    return redirect(url_for("module.index"))
