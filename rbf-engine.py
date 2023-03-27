#!/usr/bin/env python3

import logging
import click

from engine.manager import Manager
from engine.helpers import setup_logging


@click.command()
@click.option("--workers", "-w", default=1, help="Number of worker processes.")
@click.option("--debug", is_flag=True)
def cli(workers, debug):
    if debug:
        setup_logging(log_level=logging.DEBUG)
    else:
        setup_logging(log_level=logging.INFO)
    manager = Manager(num_workers=workers)
    manager.start()


if __name__ == "__main__":
    cli()
