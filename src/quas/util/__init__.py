import click

from quas.util.rev import rev


@click.group()
def app() -> None: ...


app.add_command(rev)
