import re
import string
from collections.abc import Iterable


class Alphabet:
    def __init__(self, alphabet: list[str]):
        self.alphabet: list[str] = sorted(alphabet, key=len, reverse=True)
        self.letters: set[str] = set(self.alphabet)
        self.encoding: dict[str, int] = {c: i for i, c in enumerate(self.alphabet)}

        pattern_str = "|".join(map(re.escape, self.alphabet))
        self.pattern: re.Pattern[str] = re.compile(pattern_str)

    def __contains__(self, c: str) -> bool:
        return c in self.letters

    def __len__(self):
        return len(self.alphabet)

    def __str__(self):
        return " ".join(self.alphabet)

    def encode_letter(self, char: str) -> int | None:
        return self.encoding.get(char)

    def encode(self, chars: str) -> tuple[int, ...]:
        return tuple(self.encoding[m.group()] for m in self.pattern.finditer(chars))

    def decode_letter(self, idx: int) -> str:
        return self.alphabet[idx]

    def decode(self, indices: Iterable[int]) -> str:
        return "".join(map(self.decode_letter, indices))


english_upper = Alphabet(list(string.ascii_uppercase))
