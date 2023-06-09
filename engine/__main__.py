import click

from manager import WorkerManager
from worker import Worker


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Invoked without subcommand")
    else:
        click.echo(f"Invoking subcommand {ctx.invoked_subcommand}")


@cli.command()
@click.option("--workers", "-w", type=int, default=1, help="Number of workers to spawn.")
def engine(workers):
    click.echo(f"Starting engine with {workers} workers")

    worker = Worker()
    manager = WorkerManager(worker, num_workers=workers)
    manager.start()


@cli.command()
@click.option("--port", "-p", metavar="PORT", type=int, default=5000)
@click.option("--debug/--no-debug", default=False, help="Debug mode.")
def web(port, debug):
    if debug:
        click.echo("DEBUG MODE")

    click.echo(f"Running on port {port}")


if __name__ == "__main__":
    cli()
