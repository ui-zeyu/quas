import click

from quas.crypto import affine


@click.group()
def app() -> None: ...


app.add_command(affine.bruteforce, affine.__name__.rsplit(".", 1)[-1])
