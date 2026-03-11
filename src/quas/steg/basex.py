from collections.abc import Sequence
from dataclasses import dataclass
from functools import reduce
from itertools import batched
from math import lcm

from rich.text import Text

TABLE_BASE32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
TABLE_BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


@dataclass
class BaseXPayload:
    bits: bytearray
    steg: str

    def __rich__(self) -> Text:
        bits = "".join(str(x) for x in self.bits)
        return Text.assemble(bits, self.steg)


def basex_decode(lines: Sequence[str], table: str) -> BaseXPayload:
    rank = len(table).bit_length() - 1
    num_pads = lcm(rank, 8) // rank

    bits = bytearray()
    for line in lines:
        line = line.rstrip("=")
        if len(line) % num_pads == 0:
            continue

        x = table.find(line[-1])
        num_bits = len(line) * rank % 8
        for i in reversed(range(num_bits)):
            bits.append((x >> i) & 1)

    steg = bytes(
        reduce(lambda s, x: s << 1 | x, byte, 0)
        for byte in batched(bits, 8, strict=False)
    ).decode(errors="replace")

    return BaseXPayload(bits=bits, steg=steg)
