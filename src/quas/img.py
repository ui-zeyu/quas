from pathlib import Path

import click
import numpy as np
from PIL import Image
from rich.table import Table

from quas.base import ContextObject


@click.group()
def app() -> None: ...


@app.command(help="Inspect image pixels by coordinate sampling")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option("-x", type=int, default=0, help="Starting x coordinate (default: 0)")
@click.option("-y", type=int, default=0, help="Starting y coordinate (default: 0)")
@click.option("--stepx", type=int, default=1, help="X step size (default: 1)")
@click.option("--stepy", type=int, default=1, help="Y step size (default: 1)")
@click.option(
    "-c",
    "--count",
    type=int,
    default=10,
    help="Number of pixels to display (0 for all)",
)
def inspect(
    ctx: ContextObject,
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
    count: int,
) -> None:
    console = ctx["console"]

    img = Image.open(infile).convert("RGBA")
    arr = np.array(img)
    pixels = arr[y::stepy, x::stepx]
    pixels = pixels.reshape(-1, 4)

    table = Table("No.", "RGBA", box=None, highlight=True)
    display_pixels = pixels if count == 0 else pixels[:count]
    for i, (r, g, b, a) in enumerate(display_pixels):
        table.add_row(str(i), f"[ {r}, {g}, {b}, {a} ]")
    console.print(table)


@app.command(help="Extract image pixels by coordinate sampling")
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=True)
@click.option("-x", type=int, default=0, help="Starting x coordinate (default: 0)")
@click.option("-y", type=int, default=0, help="Starting y coordinate (default: 0)")
@click.option("--stepx", type=int, default=1, help="X step size (default: 1)")
@click.option("--stepy", type=int, default=1, help="Y step size (default: 1)")
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
