from pathlib import Path

import click

from quas.commands.context import ContextObject
from quas.steg.base import TABLE_BASE32, TABLE_BASE64


def basex_factory(table: str) -> click.Command:
    @click.command(
        help=f"Extract hidden data from {table == TABLE_BASE32 and 'Base32' or 'Base64'} encoded strings",
    )
    @click.pass_obj
    @click.argument("infile", type=Path)
    def inner(ctx: ContextObject, infile: Path) -> None:
        from quas.steg.basex import perform_basex_decode

        console = ctx["console"]
        result = perform_basex_decode(infile.read_text().splitlines(), table)
        console.print(result)

    return inner


@click.group(help="Steganography tools")
def app() -> None: ...


@click.command(help="Decode zero-width character steganography")
@click.pass_obj
@click.argument("text", required=False)
@click.option(
    "-t",
    "--top",
    type=int,
    default=10,
    help="Number of top results to display",
)
def zerowidth(ctx: ContextObject, text: str | None, top: int) -> None:
    from sys import stdin

    from quas.steg.zerowidth import ZeroWidthDecoder

    console = ctx["console"]

    text = text or stdin.read()
    result = ZeroWidthDecoder.perform_crack(text, top)
    console.print(result)


app.add_command(basex_factory(TABLE_BASE32), "b32")
app.add_command(basex_factory(TABLE_BASE64), "b64")
app.add_command(zerowidth)
