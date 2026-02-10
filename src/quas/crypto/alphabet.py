import string
from collections.abc import Iterable


class Alphabet:
    def __init__(self, alphabet: list[str]):
        self.alphabet = alphabet
        self.letters = set(alphabet)
        self.encoding: dict[str, int] = {c: i for i, c in enumerate(alphabet)}

    def __contains__(self, c: str) -> bool:
        return c in self.letters

    def __len__(self):
        return len(self.alphabet)

    def __str__(self):
        return "".join(self.alphabet)

    def encode_letter(self, char: str) -> int | None:
        return self.encoding.get(char)

    def encode(self, chars: Iterable[str]) -> tuple[int, ...]:
        return tuple(filter(lambda x: x is not None, map(self.encode_letter, chars)))

    def decode_letter(self, idx: int) -> str:
        return self.alphabet[idx]

    def decode(self, indices: Iterable[int]) -> str:
        return "".join(map(self.decode_letter, indices))


english_upper = Alphabet(list(string.ascii_uppercase))
