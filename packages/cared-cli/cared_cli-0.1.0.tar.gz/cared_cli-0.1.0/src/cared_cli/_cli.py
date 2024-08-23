import click

from cared_cli import __version__, _logo, core


@click.version_option(__version__, "-V", "--version", prog_name="cared")
@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx):
    """A command line interface for managing a CaReD server."""
    if ctx.invoked_subcommand is None:
        click.echo(_logo.ascii_art)
        click.echo(app.get_help(ctx))


@click.argument("name", type=str, default="world")
@app.command(
    short_help="Says hello.",
)
def hello(name: str):
    hello_message = core.hello(name)
    click.echo(hello_message)


if __name__ == "__main__":
    app()
