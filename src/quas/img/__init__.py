import click

from quas.img.extract import extract
from quas.img.inspect import inspect


@click.group()
def app() -> None: ...


app.add_command(extract)
app.add_command(inspect)
