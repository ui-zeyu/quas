import click

from quas.behinder.aes import aes
from quas.behinder.xor import xor


@click.group()
def app() -> None: ...


app.add_command(aes)
app.add_command(xor)
