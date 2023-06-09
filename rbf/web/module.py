from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from .models import db
from .models import Module, TriggeredSubmission, TriggeredComment
from .forms import ModuleForm
from .helpers import (
    flash_form_errors, dispatch_message, publish_message, create_module
)


module_bp = Blueprint("module", __name__, url_prefix="/user")


@module_bp.route("/", methods=("GET",))
@login_required
def index():
    return render_template("module/index.html")


@module_bp.route("/modules", methods=("GET",))
@login_required
def modules():
    return render_template("module/list.html")


@module_bp.route("/module/create", methods=("GET", "POST"))
@login_required
def create():
    form = ModuleForm()
    if form.validate_on_submit():
        module = Module.query.filter(
            (Module.app_user == current_user) &
            (Module.name == form.name.data)
        ).first()
        if module is not None:
            flash("A module with that name already exists.", "error")
            return render_template("module/create.html", form=form)
        else:
            new_module = create_module(current_user, form)
            db.session.add(new_module)
            db.session.commit()
            dispatch_message("load", new_module.id)
        return redirect(url_for("module.activity", id=new_module.id))
    else:
        flash_form_errors(form)
    return render_template("module/create.html", form=form)


@module_bp.route("/module/<int:id>/", methods=("GET",))
@login_required
def detail(id):
    return redirect(url_for("module.activity", id=id))


@module_bp.route("/module/<int:id>/activity", methods=("GET",))
@login_required
def activity(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            page = max(0, request.args.get("page", 1, type=int))

            if module.stream == "submission":
                query = db.select(TriggeredSubmission).where(TriggeredSubmission.module_id == module.id).order_by(TriggeredSubmission.created.desc())
                print(query)
            elif module.stream == "comment":
                query = db.select(TriggeredComment).where(TriggeredComment.module_id == module.id).order_by(TriggeredComment.created.desc())
                print(query)

            page = db.paginate(query)

            return render_template(
                "module/activity.html",
                module=module,
                pagination=page
            )
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/delete", methods=("POST", "DELETE"))
@login_required
def delete(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            db.session.delete(module)
            db.session.commit()
            return redirect(url_for("module.index"))
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/trigger", methods=("GET", "POST"))
@login_required
def trigger(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            return render_template("module/trigger.html", module=module)
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/actions", methods=("GET", "POST"))
@login_required
def actions(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            return render_template("module/actions.html", module=module)
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/settings", methods=("GET", "POST"))
@login_required
def settings(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            return render_template("module/settings.html", module=module)
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/start", methods=("GET",))
@login_required
def start(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            dispatch_message("load", module.id)
            module.status = "STARTING"
            db.session.commit()
            return redirect(url_for("module.activity", id=id))
        else:
            abort(403)
    else:
        abort(404)


@module_bp.route("/module/<int:id>/stop", methods=("GET",))
@login_required
def stop(id):
    module = Module.query.filter(Module.id == id).first()
    if module is not None:
        if module.app_user.id == current_user.id:
            publish_message("kill", module.id)
            module.status = "STOPPING"
            db.session.commit()
            return redirect(url_for("module.activity", id=id))
        else:
            abort(403)
    else:
        abort(404)
