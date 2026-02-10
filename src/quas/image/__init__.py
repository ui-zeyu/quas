import click

from quas.image.extract import extract
from quas.image.inspect import inspect
from quas.image.lsbaes import lsbaes


@click.group()
def app() -> None: ...


app.add_command(extract)
app.add_command(inspect)
app.add_command(lsbaes)
