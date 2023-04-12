from flask import (
    Blueprint, flash, redirect, render_template, url_for
)
from flask_login import login_user, logout_user

from app import db, login
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app.helpers import flash_form_errors

bp = Blueprint("auth", __name__, url_prefix="/auth")


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        if user is not None:
            error = "Username unavailable."
            flash(error)
            return redirect(url_for("auth.register"))
        else:
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully.")
            return redirect(url_for("auth.login"))
    else:
        flash_form_errors(form)

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        error = "Incorrect username or password."
        user = User.query.filter(User.username == form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(error)
            return redirect(url_for("auth.login"))
        else:
            login_user(user)
            return redirect(url_for("module.index"))
    else:
        flash_form_errors(form)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
