"""Command-line interface."""

import click

from .engine.manager import Manager
from .engine.worker import Worker

from .app import create_app


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--workers", "-w", type=int, default=1)
def engine(workers) -> None:
    worker = Worker()
    manager = Manager(worker, num_workers=workers)
    manager.start()


@cli.command()
@click.option("--init-db/--no-init-db", default=False)
@click.option("--debug/--no-debug", default=True)
def web(init_db, debug) -> None:
    app = create_app()

    if init_db:
        from .app import db

        with app.app_context():
            db.drop_all()
            db.create_all()

    app.run(debug=debug)
