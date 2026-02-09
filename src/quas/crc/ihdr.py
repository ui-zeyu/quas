from binascii import crc32
from io import BytesIO
from pathlib import Path
from struct import pack, unpack

import click
from PIL import Image, UnidentifiedImageError

from quas.context import ContextObject

PNG_SIGNATURE = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
IHDR_CHUNK_TYPE = b"IHDR"
MAX_DIMENSION = 5000


@click.command(help="Recover PNG IHDR dimensions by bruteforcing CRC32")
@click.pass_obj
@click.argument("infile", type=Path)
@click.argument("outfile", type=Path, required=False)
@click.option(
    "--max-width",
    type=int,
    default=MAX_DIMENSION,
    help="Maximum width to search",
)
@click.option(
    "--max-height",
    type=int,
    default=MAX_DIMENSION,
    help="Maximum height to search",
)
def ihdr(
    ctx: ContextObject,
    infile: Path,
    max_width: int,
    max_height: int,
    outfile: Path | None,
) -> None:
    console = ctx["console"]

    data = infile.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("Invalid PNG signature")

    chunk_length, chunk_type = unpack(">I4s", data[8:16])
    if chunk_length != 0x0D or chunk_type != IHDR_CHUNK_TYPE:
        raise ValueError("First chunk is not IHDR")

    (width, height, ihdr_suffix, target) = unpack(">II5sI", data[16:33])
    console.print(f"[bold]Original dimensions:[/bold] {width} x {height}")
    console.print(f"[bold]Bruteforce range:[/bold] 1-{max_width} x 1-{max_height}")

    with console.status("[bold green]Bruteforcing...[/bold green]"):
        for x in range(1, max_width + 1):
            for y in range(1, max_height + 1):
                ihdr = IHDR_CHUNK_TYPE + pack(">II5s", x, y, ihdr_suffix)
                crc = crc32(ihdr) & 0xFFFFFFFF
                if crc == target:
                    chunk = b"\x00\x00\x00\x0d" + ihdr + pack(">I", crc)
                    image = PNG_SIGNATURE + chunk + data[33:]

                    try:
                        img = Image.open(BytesIO(image))
                        console.print(f"\n[green]Found: {x} x {y}[/green]")
                        return img.save(outfile) if outfile is not None else img.show()
                    except UnidentifiedImageError:
                        continue
