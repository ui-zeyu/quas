import heapq
import math
import operator
import unicodedata
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import batched, permutations

from rich.table import Table

from quas.core.protocols import CommandResult


def evaluator(text: str) -> float:
    score = 0.0
    for char in text:
        cat = unicodedata.category(char)
        if cat.startswith(("L", "N", "P", "S")):
            score += 1
        elif cat.startswith("M"):
            score += 0.5
        elif cat.startswith("C"):
            score -= 1
    return score / len(text)


@dataclass
class ZeroWidthCrackItem:
    steg: str
    charset: Sequence[str]
    score: float


@dataclass
class ZeroWidthPayload:
    items: list[ZeroWidthCrackItem]


@dataclass
class ZeroWidthResult(CommandResult[ZeroWidthPayload]):
    data: ZeroWidthPayload

    def __rich__(self) -> Table:
        table = Table("Charset", "Decoded Content", "Score", box=None)
        for item in self.data.items:
            charset_str = " ".join([repr(c).replace("'", "") for c in item.charset])
            table.add_row(charset_str, item.steg, f"{item.score:.2f}")
        return table


class ZeroWidthDecoder:
    def __init__(self, charset: Sequence[str]) -> None:
        self.charset: Sequence[str] = charset
        self.radix: int = len(self.charset)
        self.codelength: int = math.ceil(math.log(65536, self.radix))
        self.decode_map = {c: str(i) for i, c in enumerate(charset)}

    def decode(self, text: str) -> str | None:
        digits = "".join(x for c in text if (x := self.decode_map.get(c)))
        try:
            codes = bytearray()
            for chunk in batched(digits, self.codelength, strict=False):
                code = int("".join(chunk), self.radix)
                codes.extend(code.to_bytes(2, byteorder="big"))
            return codes.decode("utf-16be").strip()
        except UnicodeDecodeError, OverflowError:
            return None

    @classmethod
    def crack(cls, text: str) -> Iterator[tuple[str, Sequence[str], float]]:
        text = "".join(c for c in text if unicodedata.category(c) == "Cf")
        zwcs = set(text)

        for r in range(2, len(zwcs) + 1):
            for charset in permutations(zwcs, r):
                if steg := cls(charset).decode(text):
                    yield steg, charset, evaluator(steg)

    @classmethod
    def perform_crack(cls, text: str, top: int) -> ZeroWidthResult:
        results = cls.crack(text)
        items = []
        for steg, charset, score in heapq.nlargest(
            top, results, operator.itemgetter(2)
        ):
            items.append(ZeroWidthCrackItem(steg, charset, score))
        return ZeroWidthResult(ZeroWidthPayload(items))
