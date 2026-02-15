from collections import UserList
from random import Random
from typing import Self, override

from quas.analysis.alphabet import Alphabet
from quas.crypto.base import Cipher, Key


class SubstituteKey(UserList, Key):
    @classmethod
    def random(cls, rng: Random) -> Self:
        key = cls(range(26))
        rng.shuffle(key.data)
        return key

    def __hash__(self):
        return hash(tuple(self.data))

    def swap(self, x: int, y: int) -> None:
        self.data[x], self.data[y] = self.data[y], self.data[x]


class SubstitutionCipher(Cipher):
    def __init__(self, calphabet: Alphabet, key: SubstituteKey) -> None:
        self.key: SubstituteKey = key
        self._calphabet: Alphabet = calphabet

    @override
    def calphabet(self) -> Alphabet:
        return self._calphabet

    @override
    def decrypt_letter(self, x: int) -> int:
        return self.key[x]

    @override
    def decrypt(self, ciphertext: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(self.key[x] for x in ciphertext)
