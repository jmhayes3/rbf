#!/usr/bin/env python3

import logging
import click

from engine.manager import Manager


@click.command()
@click.option("--workers", "-w", default=1, help="Number of worker processes.")
def cli(workers):
    manager = Manager(num_workers=workers)
    manager.start()


if __name__ == "__main__":
    cli()
