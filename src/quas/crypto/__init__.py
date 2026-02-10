import click

from quas.crypto import affine, substitute, xor


@click.group()
def app() -> None: ...


app.add_command(affine.bruteforce, "affine")
app.add_command(substitute.crack, "sub")
app.add_command(xor.crack, "xor")
