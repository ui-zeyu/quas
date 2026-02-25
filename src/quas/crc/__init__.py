import click

from quas.crc.ihdr import ihdr
from quas.crc.zip import zip


@click.group(help="CRC and checksum tools")
def app() -> None: ...


app.add_command(zip)
app.add_command(ihdr)
