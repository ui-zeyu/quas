import click

from quas.pdf.stream import stream


@click.group(help="PDF analysis tools")
def app() -> None: ...


app.add_command(stream)
