from flask import (
    Blueprint, flash, redirect, render_template, url_for
)
from flask_login import LoginManager, login_user, logout_user

from .forms import RegistrationForm, LoginForm
from .models import db, AppUser
from .helpers import flash_form_errors


auth_bp= Blueprint("auth", __name__, url_prefix="/auth")

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    return AppUser.query.get(int(id))


@auth_bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = AppUser.query.filter(AppUser.username == form.username.data).first()
        if user is not None:
            error = "Username unavailable."
            flash(error)
            return redirect(url_for("auth.register"))
        else:
            new_user = AppUser(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully.")
            return redirect(url_for("auth.login"))
    else:
        flash_form_errors(form)

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        error = "Incorrect username or password."
        user = AppUser.query.filter(AppUser.username == form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(error)
            return redirect(url_for("auth.login"))
        else:
            login_user(user)
            return redirect(url_for("module.index"))
    else:
        flash_form_errors(form)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
