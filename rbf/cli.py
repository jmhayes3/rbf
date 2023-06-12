"""Command-line interface."""

import click

from .engine.manager import Manager
from .engine.worker import Worker


CONTEXT_SETTINGS = dict(
    default_map = {
        "engine": {"workers": 2},
        "web": {
            "port": 5001,
            "debug": True,
        },
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
@click.option("--port", type=int, default=5000)
@click.option("--debug/--no-debug", default=False)
def web(port, debug):
    click.echo(f"DEBUG MODE: {debug}")
    click.echo(f"Serving on port {port}")


if __name__ == "__main__":
    cli()
