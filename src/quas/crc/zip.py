import itertools
from binascii import crc32
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial

from rich.table import Table

from quas.core.protocols import CommandResult


@dataclass
class ZipPayload:
    results: dict[int, list[str]]
    crc2file: dict[int, str]


@dataclass
class ZipResult(CommandResult[ZipPayload]):
    data: ZipPayload

    def __rich__(self) -> Table:
        table = Table("File", "CRC32", "Found", box=None, highlight=True)
        for crc, contents in self.data.results.items():
            table.add_row(
                self.data.crc2file.get(crc, "Unknown"),
                f"{crc:08X}",
                ", ".join(contents),
            )
        return table


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
    crc2file: dict[int, str],
) -> ZipResult:
    if jobs == 1 or size < 4:
        results = _worker(b"", size, targets, charset)
        return ZipResult(ZipPayload(results=results, crc2file=crc2file))

    results = defaultdict(list)
    worker = partial(_worker, size=size - 1, targets=targets, charset=charset)
    with ProcessPoolExecutor(jobs) as e:
        for result in e.map(worker, (bytes([x]) for x in charset)):
            for k, v in result.items():
                results[k].extend(v)
    return ZipResult(ZipPayload(results=results, crc2file=crc2file))
