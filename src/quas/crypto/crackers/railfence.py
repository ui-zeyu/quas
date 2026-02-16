from collections.abc import Generator
from itertools import count, islice
from typing import override

import numpy as np

from quas.analysis import english_upper
from quas.crypto.base import BruteForceCracker, Result
from quas.crypto.ciphers.railfence import RailFenceCipher, RailFenceKey


class RailFenceCracker(BruteForceCracker[RailFenceKey, str]):
    @override
    def cipher(self, key: RailFenceKey) -> RailFenceCipher:
        return RailFenceCipher(key)

    @override
    def keyspace(self) -> Generator[RailFenceKey]:
        for x in count(2):
            yield RailFenceKey(x)

    @override
    def crack(self, ciphertext: str) -> Generator[Result[RailFenceKey]]:
        max_rails = len(ciphertext) >> 1
        for key in islice(self.keyspace(), max_rails):
            cipher = self.cipher(key)
            plaintext = cipher.decrypt(ciphertext)
            indices = np.array(english_upper.encode(plaintext), dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            yield Result(key, score)
