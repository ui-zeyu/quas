import click

from quas.util.rev import rev


@click.group(help="Utility tools")
def app() -> None: ...


app.add_command(rev)
