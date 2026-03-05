from pathlib import Path

import click

from quas.context import ContextObject


@click.group(help="Image steganography tools")
def app() -> None: ...


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
    from quas.image.extract import extract_pixels

    img = extract_pixels(infile, x, y, stepx, stepy)
    img.save(outfile) if outfile else img.show()


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
    import numpy as np
    from PIL import Image
    from rich.table import Table

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

    import numpy as np

    from quas.image.lsbaes import analyse as lsbaes_analyse
    from quas.image.lsbaes import crack, extract_lsb_bits, unpack_iv_ct

    console = ctx["console"]
    if workers is None:
        workers = os.cpu_count() or 12

    bits = extract_lsb_bits(image_path)
    bytes_data = np.packbits(bits)
    iv, ct = unpack_iv_ct(console, bytes_data)
    lsbaes_analyse(bits)

    if result := crack(iv, ct, wordlist, workers):
        console.print(f"[bold]Password found:[/bold] {result.password}")
        console.print(f"[bold]Decrypted text:[/bold] {result.plaintext}")
    else:
        console.print("[bold red]No valid password found[/bold red]")


@click.command(
    help="Extract single image blind watermark using frequency domain analysis"
)
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
@click.option(
    "-m",
    "--mode",
    type=click.Choice(
        ["DFT_RESIZE", "DFT_PAD", "DFT_CROP", "DCT"], case_sensitive=False
    ),
    default="DFT_RESIZE",
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
    ctx: ContextObject,
    infile: Path,
    outfile: Path | None,
    mode: str,
    brightness: float,
) -> None:
    from PIL import Image

    from quas.image.spbwm import Mode as SPBWMMode

    image = Image.open(infile)
    mode_enum = SPBWMMode[mode.upper()]
    extractor = mode_enum.to_extractor(image, brightness)
    watermark = extractor.extract()
    watermark.save(outfile) if outfile else watermark.show()


@click.command(help="Extract double image blind watermark")
@click.pass_obj
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
    ctx: ContextObject,
    seed: int,
    old: bool,
    original: Path,
    watermarked: Path,
    outfile: Path | None,
) -> None:
    from quas.image.dpbwm import DoublePictureBlindWatermarkExtractor

    extractor = DoublePictureBlindWatermarkExtractor(original, watermarked, seed, old)
    watermark = extractor.extract()
    watermark.save(outfile) if outfile else watermark.show()


app.add_command(extract)
app.add_command(inspect)
app.add_command(lsbaes)
app.add_command(spbwm)
app.add_command(dpbwm)
