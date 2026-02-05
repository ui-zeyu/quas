from functools import reduce
from itertools import batched
from math import lcm
from pathlib import Path

import click

from quas.base import ContextObject

TABLE_BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
TABLE_BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


@click.group()
def app() -> None: ...


def basex(table: str) -> click.Command:
    @click.command(
        help=f"Extract hidden data from {table == TABLE_BASE32 and 'Base32' or 'Base64'} encoded strings",
    )
    @click.pass_obj
    @click.argument("infile", type=Path)
    def inner(ctx: ContextObject, infile: Path) -> None:
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

        steg = bytes(
            reduce(lambda s, x: s << 1 | x, byte, 0)
            for byte in batched(bits, 8, strict=False)
        ).decode(errors="replace")
        console.print(steg)

    return inner


for cmd, table in (("b32", TABLE_BASE32), ("b64", TABLE_BASE64)):
    app.add_command(basex(table), cmd)
