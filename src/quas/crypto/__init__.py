import click

from quas.crypto import affine, substitute


@click.group()
def app() -> None: ...


app.add_command(affine.bruteforce, "affine")
app.add_command(substitute.crack, "sub")
