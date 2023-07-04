"""Command-line interface."""

import click

from .engine.server import Server

from .web import create_app


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--workers", "-w", type=int, default=1)
def engine(workers) -> None:
    server = Server()
    server.start()


@cli.command()
@click.option("--debug/--no-debug", default=True)
def web(debug) -> None:
    app = create_app()
    app.run(debug=debug)
