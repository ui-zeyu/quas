import click

from quas.image.dpbwm import dpbwm
from quas.image.extract import extract
from quas.image.inspect import inspect
from quas.image.lsbaes import lsbaes
from quas.image.spbwm import spbwm


@click.group(help="Image steganography tools")
def app() -> None: ...


app.add_command(extract)
app.add_command(inspect)
app.add_command(lsbaes)
app.add_command(spbwm)
app.add_command(dpbwm)
