from collections.abc import Generator
from typing import override

from quas.crypto.base import BruteForceCracker
from quas.crypto.ciphers import AffineCipher, AffineKey


class AffineCracker(BruteForceCracker[AffineKey]):
    @override
    def cipher(self, key: AffineKey) -> AffineCipher:
        return AffineCipher(key)

    @override
    def keyspace(self) -> Generator[AffineKey]:
        for a in AffineCipher.MOD_INVERSES:
            for b in range(26):
                yield AffineKey(a, b)
