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
    from struct import unpack

    from quas.crc.ihdr import recover_ihdr_dimensions

    console = ctx["console"]

    data = infile.read_bytes()

    # Extract original dimensions to show the user
    try:
        orig_w, orig_h = unpack(">II", data[16:24])
        console.print(f"[bold]Original dimensions:[/bold] {orig_w} x {orig_h}")
        console.print(f"[bold]Bruteforce range:[/bold] 1-{max_width} x 1-{max_height}")
    except Exception:
        pass

    with console.status("[bold green]Bruteforcing...[/bold green]"):
        try:
            result = recover_ihdr_dimensions(data, max_width, max_height)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            return

    if result:
        console.print(f"\n[green]Found: {result.width} x {result.height}[/green]")
        if outfile:
            result.image.save(outfile)
        else:
            result.image.show()
    else:
        console.print("\n[red]Failed to find matching dimensions.[/red]")


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
