from pathlib import Path

import click

from quas.context import ContextObject
from quas.steg.base import TABLE_BASE32, TABLE_BASE64


def basex_factory(table: str) -> click.Command:
    @click.command(
        help=f"Extract hidden data from {table == TABLE_BASE32 and 'Base32' or 'Base64'} encoded strings",
    )
    @click.pass_obj
    @click.argument("infile", type=Path)
    def inner(ctx: ContextObject, infile: Path) -> None:
        from functools import reduce
        from itertools import batched
        from math import lcm

        console = ctx["console"]
        rank = len(table).bit_length() - 1
        num_pads = lcm(rank, 8) // rank

        bits = bytearray()
        for line in infile.read_text().splitlines():
            line = line.rstrip("=")
            if len(line) % num_pads == 0:
                continue

            x = table.find(line[-1])
            num_bits = len(line) * rank % 8
            for i in reversed(range(num_bits)):
                bits.append((x >> i) & 1)
        console.print(*(str(x) for x in bits), sep="")

        steg_data = bytes(
            reduce(lambda s, x: s << 1 | x, byte, 0)
            for byte in batched(bits, 8, strict=False)
        ).decode(errors="replace")
        console.print(steg_data)

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
    import heapq
    import operator
    from sys import stdin

    from rich.table import Table

    from quas.steg.zerowidth import ZeroWidthDecoder

    console = ctx["console"]

    text = text or stdin.read()
    results = ZeroWidthDecoder.crack(text)

    table = Table("Charset", "Decoded Content", "Score", box=None)
    for steg, charset, score in heapq.nlargest(top, results, operator.itemgetter(2)):
        charset_str = " ".join([repr(c).replace("'", "") for c in charset])
        table.add_row(charset_str, steg, f"{score:.2f}")
    console.print(table)


app.add_command(basex_factory(TABLE_BASE32), "b32")
app.add_command(basex_factory(TABLE_BASE64), "b64")
app.add_command(zerowidth)
