import click

from quas.crypto import affine, analyse, substitute, xor


@click.group()
def app() -> None: ...


app.add_command(affine.bruteforce, "affine")
app.add_command(analyse.analyse, "analyse")
app.add_command(substitute.crack, "sub")
app.add_command(xor.crack, "xor")
