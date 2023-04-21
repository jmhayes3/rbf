import click

from engine.manager import Manager


@click.group()
def engine():
    pass


@engine.command()
@click.option("--workers", "-w", default=1, help="Number of workers to spawn.")
@click.argument("address", nargs=1, type=click.Path())
def start(workers, address):
    click.echo(f"Num workers: {workers}")
    click.echo(f"Address: {address}")

    # manager = Manager(num_workers=workers)
    # manager.start()


if __name__ == "__main__":
    engine()
