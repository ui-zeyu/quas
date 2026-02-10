import click

from quas.steg.base import TABLE_BASE32, TABLE_BASE64, basex


@click.group()
def app() -> None: ...


app.add_command(basex(TABLE_BASE32), "b32")
app.add_command(basex(TABLE_BASE64), "b64")
