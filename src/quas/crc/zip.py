import itertools
from binascii import crc32
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial


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
