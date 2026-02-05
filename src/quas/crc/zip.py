import itertools
import os
import string
import zipfile
from binascii import crc32
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

import click
import toolz
from rich.table import Table

from quas.base import ContextObject


def _worker(
    prefix: bytes,
    size: int,
    targets: set[int],
    charset: bytes,
) -> dict[int, list[str]]:
    results = defaultdict(list)
    for combo in itertools.product(charset, repeat=size):
        curr = prefix + bytes(combo)
        crc = crc32(curr) & 0xFFFFFFFF
        if crc in targets:
            results[crc].append(curr.decode())
    return results


def bruteforce(
    size: int,
    targets: set[int],
    charset: bytes,
    jobs: int,
) -> dict[int, list[str]]:
    if jobs == 1 or size < 4:
        return _worker(b"", size, targets, charset)

    results = defaultdict(list)
    worker = partial(_worker, size=size - 1, targets=targets, charset=charset)
    with ProcessPoolExecutor(jobs) as e:
        for result in e.map(worker, (bytes([x]) for x in charset)):
            for k, v in result.items():
                results[k].extend(v)
    return results


@click.command(help="Bruteforce ZIP filenames by CRC32")
@click.pass_obj
@click.argument("infile", type=Path)
@click.option("-s", "--size", type=int, required=True, help="Target file size to match")
@click.option(
    "-c",
    "--charset",
    type=str,
    default=string.printable.strip(),
    help="Character set for bruteforce",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=os.cpu_count(),
    help="Number of jobs to run",
)
def zip(ctx: ContextObject, infile: Path, size: int, charset: str, jobs: int) -> None:
    console = ctx["console"]

    charset: bytes = f" {charset} ".encode()
    alphabet = bytearray()
    for p, x, n in toolz.sliding_window(3, charset):
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
