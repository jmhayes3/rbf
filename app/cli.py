import csv
import click

from flask import Blueprint

from app import db
from app.models import User

bp = Blueprint("commands", __name__, cli_group=None)


@bp.cli.command("create_db")
def create():
    db.create_all()
    click.echo("DB created")


@bp.cli.command("drop_db")
def drop():
    db.drop_all()
    click.echo("DB dropped")


@bp.cli.command("create_user")
@click.option("--name", "-n")
@click.option("--email", "-e")
@click.option("--password", "-p")
def create_user(name, email, password):
    user = User(username=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo("User {} created".format(name))
