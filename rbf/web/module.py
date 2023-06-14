import json
import zmq

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app
)
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from .models import db
from .forms import ModuleForm
from .models import Module, TriggeredSubmission, TriggeredComment
from .helpers import flash_form_errors


module_bp = Blueprint("module", __name__, url_prefix="/user")


def publish_message(context, payload):
    uri = current_app.config["ENGINE_URI"]
    ctx = zmq.Context()
    publisher = ctx.socket(zmq.PUSH)
    try:
        publisher.connect(uri)
        publisher.send_json({
            "context": context,
            "payload": payload
        })
    except Exception as e:
        raise e
    finally:
        publisher.disconnect(uri)
        publisher.close()
        ctx.term()


def create_module(current_user, form):
    print(form.data)

    fields = []
    if form.title.data:
        fields.append("title")
    if form.body.data:
        fields.append("body")

    components = []
    if form.keywords.data[0] != "":
        keyword_component = {
            "type": "keyword",
            "keywords": form.keywords.data,
            "fields": fields,
            "require_all": form.require_all.data,
            "case": form.case.data
        }
        components.append(keyword_component)

    trigger = dict(stream=form.stream.data)
    if form.targets.data[0] == "":
        trigger["targets"] = "all"
    else:
        trigger["targets"] = form.targets.data

    if components:
        trigger["components"] = components

    module = Module(
        trigger=json.dumps(trigger)
    )
    module.user = current_user
    module.name = form.name.data
    module.stream = form.stream.data

    return module


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
            (Module.user == current_user) &
            (Module.name == form.name.data)
        ).first()
        if module is not None:
            flash("A module with that name already exists.", "error")
            return render_template("module/create.html", form=form)
        else:
            new_module = create_module(current_user, form)
            db.session.add(new_module)
            db.session.commit()
            publish_message("load", new_module.id)
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
        if module.user.id == current_user.id:
            page = max(0, request.args.get("page", 1, type=int))
            per_page = max(
                5,
                min(request.args.get("per_page", 10, type=int), 100)
            )

            if module.stream == "submission":
                query = db.select(TriggeredSubmission, Module).where(TriggeredSubmission.module_id == module.id).order_by(TriggeredSubmission.created.desc())
                print(query)
            elif module.stream == "comment":
                query = db.select(TriggeredComment, Module).where(TriggeredComment.module_id == module.id).order_by(TriggeredComment.created.desc())
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
        if module.user.id == current_user.id:
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
        if module.user.id == current_user.id:
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
        if module.user.id == current_user.id:
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
        if module.user.id == current_user.id:
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
        if module.user.id == current_user.id:
            publish_message("load", module.id)
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
        if module.user.id == current_user.id:
            publish_message("kill", module.id)
            module.status = "STOPPING"
            db.session.commit()
            return redirect(url_for("module.activity", id=id))
        else:
            abort(403)
    else:
        abort(404)
