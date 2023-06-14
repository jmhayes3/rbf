from flask_wtf import FlaskForm
from wtforms import (
    validators, StringField, PasswordField, BooleanField
)

from .fields import ListField


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[validators.Length(min=3, max=25)]
    )
    email = StringField(
        "Email",
        validators=[validators.Length(min=6, max=320)]
    )
    password = PasswordField(
        "Password",
        validators=[
            validators.Length(min=6, max=25),
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match.")
        ]
    )
    confirm = PasswordField("Confirm password")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[validators.Length(min=3, max=25)]
    )
    password = PasswordField(
        "Password",
        validators=[validators.DataRequired()]
    )


class ModuleForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[validators.DataRequired()]
    )
    stream = StringField(
        "Stream",
        validators=[validators.DataRequired()]
    )
    title = BooleanField(
        "Title",
        validators=[validators.Optional()]
    )
    body = BooleanField(
        "Body",
        validators=[validators.Optional()]
    )
    case = BooleanField(
        "Case",
        validators=[validators.Optional()]
    )
    require_all = BooleanField(
        "Require All",
        validators=[validators.Optional()]
    )
    targets = ListField(
        "Targets",
        validators=[validators.Optional()]
    )
    keywords = ListField(
        "Keywords",
        validators=[validators.Optional()]
    )
