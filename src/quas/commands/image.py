from pathlib import Path

import click

from quas.commands.context import ContextObject
from quas.image.spbwm import Mode


@click.group(help="Image steganography tools")
def app() -> None: ...


@click.command(help="Extract image pixels by coordinate sampling")
@click.option("-x", type=int, default=0, help="Starting x coordinate (default: 0)")
@click.option("-y", type=int, default=0, help="Starting y coordinate (default: 0)")
@click.option("--stepx", type=int, default=1, help="X step size (default: 1)")
@click.option("--stepy", type=int, default=1, help="Y step size (default: 1)")
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
def extract(
    infile: Path,
    x: int,
    y: int,
    stepx: int,
    stepy: int,
    outfile: Path | None,
) -> None:
    from quas.image.extract import extract_pixels

    image = extract_pixels(infile, x, y, stepx, stepy).data
    image.save(outfile) if outfile else image.show()


@click.command(help="Inspect image pixels by coordinate sampling")
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
    from quas.image.inspect import perform_inspect

    console = ctx["console"]
    result = perform_inspect(infile, x, y, stepx, stepy, count)
    console.print(result)


@click.command(
    help="Extract AES-encrypted data hidden in LSB bits and brute-force password"
)
@click.pass_obj
@click.argument("image_path", type=Path)
@click.argument("wordlist", type=Path)
@click.option(
    "-w",
    "--workers",
    type=int,
    help="Number of worker processes",
)
def lsbaes(
    ctx: ContextObject, image_path: Path, wordlist: Path, workers: int | None
) -> None:
    import os

    from quas.image.lsbaes import perform_lsbaes

    console = ctx["console"]
    if workers is None:
        workers = os.cpu_count() or 12

    result = perform_lsbaes(image_path, wordlist, workers, console)
    console.print(result)


@click.command(
    help="Extract single image blind watermark using frequency domain analysis"
)
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(Mode, case_sensitive=False),
    default=Mode.DFT_RESIZE,
    help="Processing mode",
)
@click.option(
    "-b",
    "--brightness",
    type=float,
    default=50,
    help="Watermark brightness enhancement factor",
)
def spbwm(
    infile: Path,
    outfile: Path | None,
    mode: Mode,
    brightness: float,
) -> None:
    image = Mode.perform(infile, mode, brightness).data
    image.save(outfile) if outfile else image.show()


@click.command(help="Extract double image blind watermark")
@click.option(
    "-s",
    "--seed",
    default=20160930,
    help="Default seed for BlindWaterMark",
)
@click.option("--old", is_flag=True, help="Use Python2 random algorithm")
@click.argument("original", type=Path)
@click.argument("watermarked", type=Path)
@click.argument("outfile", type=Path, required=False)
def dpbwm(
    seed: int,
    old: bool,
    original: Path,
    watermarked: Path,
    outfile: Path | None,
) -> None:
    from quas.image.dpbwm import DoublePictureBlindWatermarkExtractor

    image = DoublePictureBlindWatermarkExtractor.perform(
        original,
        watermarked,
        seed,
        old,
    ).data
    image.save(outfile) if outfile else image.show()


app.add_command(extract)
app.add_command(inspect)
app.add_command(lsbaes)
app.add_command(spbwm)
app.add_command(dpbwm)
