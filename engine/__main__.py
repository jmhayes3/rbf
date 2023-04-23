import click

from engine.manager import Manager


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("Invoked without subcommand")
    elif ctx.invoked_subcommand is True:
        click.echo("So true")
    else:
        click.echo(f"Invoking subcommand {ctx.invoked_subcommand}")


@cli.command()
@click.option("--address", metavar="ADDRESS", type=click.Path(), default="")
@click.option("--port", metavar="PORT", type=int, default=8000)
def engine(address, port):
    click.echo("Starting engine...")

    # manager = Manager(num_workers=1)
    # manager.start()


@cli.command()
@click.option("--address", metavar="ADDRESS", type=click.Path(), default="localhost", help="Address")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def web(address, debug):
    if debug:
        click.echo("Running in debug mode!")

    click.echo(f"Web application is running at: {address}")


def main():
    cli()


if __name__ == "__main__":
    main()
