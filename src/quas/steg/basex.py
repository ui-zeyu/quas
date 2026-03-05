from dataclasses import dataclass
from functools import reduce
from itertools import batched
from math import lcm

from rich.console import Group
from rich.text import Text

from quas.core.protocols import CommandResult


@dataclass
class BaseXPayload:
    bits: bytearray
    steg_data: str


@dataclass
class BaseXResult(CommandResult[BaseXPayload]):
    data: BaseXPayload

    def __rich__(self) -> Group:
        bit_str = "".join(str(x) for x in self.data.bits)
        return Group(Text(bit_str), Text(self.data.steg_data))


def perform_basex_decode(lines: list[str], table: str) -> BaseXResult:
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

    steg_data = bytes(
        reduce(lambda s, x: s << 1 | x, byte, 0)
        for byte in batched(bits, 8, strict=False)
    ).decode(errors="replace")

    return BaseXResult(BaseXPayload(bits=bits, steg_data=steg_data))
