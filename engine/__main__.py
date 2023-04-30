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
@click.option("--port", metavar="PORT", type=int, default=8000)
def engine(port):
    click.echo(f"Starting engine on port: {port}")
    manager = Manager(num_workers=1)
    manager.start()


@cli.command()
@click.option("--port", metavar="PORT", type=int, default=8000)
@click.option("--debug", is_flag=True, help="Run in debug mode")
def web(port, debug):
    click.echo(f"Running on port: {port}")
    if debug:
        click.echo("DEBUG MODE!")

def main():
    cli()


if __name__ == "__main__":
    main()
