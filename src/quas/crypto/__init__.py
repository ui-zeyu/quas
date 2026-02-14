import click

from quas.crypto import affine, analyse, caesar, substitute, xor


@click.group()
def app() -> None: ...


app.add_command(affine.crack, "affine")
app.add_command(analyse.analyse, "analyse")
app.add_command(caesar.crack, "caesar")
app.add_command(substitute.crack, "sub")
app.add_command(xor.crack, "xor")
