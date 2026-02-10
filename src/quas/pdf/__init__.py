import click

from quas.pdf.stream import stream


@click.group()
def app() -> None: ...


app.add_command(stream)
