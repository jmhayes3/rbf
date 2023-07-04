import json

import zmq

from flask import flash, current_app

from .models import Module


def flash_form_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                "{}: {}".format(getattr(form, field).label.text, error),
                "error"
            )


def dispatch_message(context, payload):
    uri = current_app.config["ENGINE_URI"]
    ctx = zmq.Context()
    dispatcher = ctx.socket(zmq.PUB)
    try:
        dispatcher.connect(uri)
        dispatcher.send_json({
            "context": context,
            "payload": payload
        })
    except Exception as e:
        raise e
    finally:
        dispatcher.disconnect(uri)
        dispatcher.close()
        ctx.term()


def create_module(current_user, form):
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
