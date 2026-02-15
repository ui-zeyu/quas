from collections.abc import Generator, Sequence
from typing import override

from quas.crypto.base import BruteForceCracker
from quas.crypto.ciphers import CaesarCipher, CaesarKey


class CaesarCracker(BruteForceCracker[CaesarKey, Sequence[int]]):
    @override
    def cipher(self, key: CaesarKey) -> CaesarCipher:
        return CaesarCipher(key)

    @override
    def keyspace(self) -> Generator[CaesarKey]:
        for x in range(26):
            yield CaesarKey(x)
