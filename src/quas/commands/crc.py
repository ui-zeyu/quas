from pathlib import Path

import click

from quas.context import ContextObject
from quas.crc.ihdr import MAX_DIMENSION


@click.group(help="CRC and checksum tools")
def app() -> None: ...


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
    from binascii import crc32
    from io import BytesIO
    from struct import pack, unpack

    from PIL import Image, UnidentifiedImageError

    from quas.crc.ihdr import IHDR_CHUNK_TYPE, PNG_SIGNATURE

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
                ihdr_data = IHDR_CHUNK_TYPE + pack(">II5s", x, y, ihdr_suffix)
                crc = crc32(ihdr_data) & 0xFFFFFFFF
                if crc == target:
                    chunk = b"\x00\x00\x00\x0d" + ihdr_data + pack(">I", crc)
                    image_data = PNG_SIGNATURE + chunk + data[33:]

                    try:
                        img = Image.open(BytesIO(image_data))
                        console.print(f"\n[green]Found: {x} x {y}[/green]")
                        return img.save(outfile) if outfile is not None else img.show()
                    except UnidentifiedImageError:
                        continue


@click.command(help="Bruteforce ZIP filenames by CRC32")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option("-s", "--size", type=int, required=True, help="Target file size to match")
@click.option(
    "-c",
    "--charset",
    type=str,
    default="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ ",
    help="Character set for bruteforce",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=None,
    help="Number of jobs to run",
)
def zip_cmd(
    ctx: ContextObject, infile: Path, size: int, charset: str, jobs: int | None
) -> None:
    import os
    import zipfile

    import toolz
    from rich.table import Table

    from quas.crc.zip import bruteforce

    console = ctx["console"]
    if jobs is None:
        jobs = os.cpu_count() or 1

    charset_bytes: bytes = f" {charset} ".encode()
    alphabet = bytearray()
    for p, x, n in toolz.sliding_window(3, charset_bytes):
        if x == ord("-") and p < n:
            alphabet.extend(range(p + 1, n))
        else:
            alphabet.append(x)
    console.print(f"Charset: [bold red]{alphabet.decode()}[/bold red]\n")

    if size > 4:
        cmd = f"hashcat -O -a 3 -m 11500 --keep-guessing <CRC32>:{'0' * 8 + ' ' + '?a' * size}"
        console.print(f"For large size try Hashcat:\n [bold cyan]{cmd}[/bold cyan]\n")

    with zipfile.ZipFile(infile, "r") as zf:
        crc2file = {f.CRC: f.filename for f in zf.infolist() if f.file_size == size}
        results = bruteforce(size, set(crc2file.keys()), bytes(alphabet), jobs)

        table = Table("File", "CRC32", "Found", box=None, highlight=True)
        for crc, contents in results.items():
            table.add_row(crc2file[crc], f"{crc:08X}", ", ".join(contents))
        console.print(table)


app.add_command(ihdr)
app.add_command(zip_cmd, "zip")
