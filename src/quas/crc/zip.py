import binascii
import contextlib
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import product
from multiprocessing import Pool
from typing import TypedDict

from rich.console import Group
from rich.table import Table


class JobResult(TypedDict):
    crc: int
    data: str


@dataclass
class ZipPayload:
    results: dict[int, list[str]] = field(default_factory=lambda: defaultdict(list))
    crc2file: dict[int, str] = field(default_factory=dict)

    def __rich__(self) -> Group:
        table = Table(title="Zip CRC32 Bruteforce Results")
        table.add_column("Filename", justify="left", style="cyan")
        table.add_column("CRC32", justify="right", style="magenta")
        table.add_column("Content", justify="left", style="green")

        for crc, contents in self.results.items():
            for content in contents:
                table.add_row(
                    self.crc2file.get(crc, "Unknown"), f"0x{crc:08X}", content
                )

        return Group(table)


def _worker(
    args: tuple[bytes, int, set[int], bytes],
) -> ZipPayload:
    prefix, size, targets, charset = args
    recovered = ZipPayload()
    for p in product(charset, repeat=size):
        data = prefix + bytes(p)
        crc = binascii.crc32(data) & 0xFFFFFFFF
        if crc in targets:
            with contextlib.suppress(UnicodeDecodeError):
                recovered.results[crc].append(data.decode())
    return recovered


def crack(
    size: int,
    targets: set[int],
    charset: bytes,
    jobs: int = 1,
    crc2file: dict[int, str] | None = None,
) -> ZipPayload:
    args = []
    if jobs == 1:
        args.append((b"", size, targets, charset))
    else:
        for c in charset:
            args.append((bytes([c]), size - 1, targets, charset))

    with Pool(jobs) as pool:
        worker_results = pool.map(_worker, args)

    results = ZipPayload()
    for w_res in worker_results:
        for k, v in w_res.results.items():
            results.results[k].extend(v)

    results.crc2file = crc2file or {}

    return results
