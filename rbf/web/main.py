from flask import (
    Blueprint, redirect, render_template, url_for
)


main_bp = Blueprint("main", __name__, url_prefix="/")


@main_bp.route("/", methods=("GET",))
@main_bp.route("/index", methods=("GET",))
def index():
    return render_template("module/index.html")
