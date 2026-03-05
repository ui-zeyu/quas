import math
import unicodedata
from collections.abc import Iterator, Sequence
from itertools import batched, permutations


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


class ZeroWidthDecoder:
    def __init__(self, charset: Sequence[str]):
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
