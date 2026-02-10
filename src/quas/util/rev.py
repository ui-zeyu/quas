import subprocess
from pathlib import Path

import click

from quas.context import ContextObject


@click.command(help="Reverse bytes of a file")
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument(
    "outfile",
    type=Path,
    default="-",
)
def rev(ctx: ContextObject, infile: Path, outfile: Path) -> None:
    data = bytes(reversed(infile.read_bytes()))
    if outfile == Path("-"):
        _ = subprocess.run(["hexyl"], input=data)
    else:
        _ = outfile.write_bytes(data)
