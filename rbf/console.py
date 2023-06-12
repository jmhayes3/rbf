"""Command-line interface."""
import subprocess
import sys

import click

from .engine.manager import Manager
from .engine.worker import Worker

from .app import create_app


CONTEXT_SETTINGS = dict(
    default_map = {
        "engine": {"workers": 2},
        "web": {"workers": 2},
    }
)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.option("--workers", "-w", type=int, default=1)
def engine(workers):
    click.echo(f"Workers: {workers}")

    worker = Worker()
    manager = Manager(worker, num_workers=workers)
    manager.start()


@cli.command()
@click.option("--workers", "-w", type=int, default=1)
def web(workers):
    click.echo(f"Workers: {workers}")
    
    server = create_app()
    server.run()

    # launch gunicorn as subprocess

if __name__ == "__main__":
    cli()
