from pathlib import Path

import click
import numpy as np
from PIL import Image

from quas.context import ContextObject


@click.command(help="Extract image pixels by coordinate sampling")
@click.pass_obj
@click.option("-x", type=int, default=0, help="Starting x coordinate (default: 0)")
@click.option("-y", type=int, default=0, help="Starting y coordinate (default: 0)")
@click.option("--stepx", type=int, default=1, help="X step size (default: 1)")
@click.option("--stepy", type=int, default=1, help="Y step size (default: 1)")
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
def extract(
    ctx: ContextObject,
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
    outfile: Path | None,
) -> None:
    img = Image.open(infile).convert("RGBA")
    arr = np.array(img)
    pixels = arr[y::stepy, x::stepx]
    img = Image.fromarray(pixels, "RGBA")
    img.save(outfile) if outfile is not None else img.show()
