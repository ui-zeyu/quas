from collections.abc import Iterator
from itertools import count, islice
from typing import override

import numpy as np

from quas.analysis import english_upper
from quas.crypto.base import BruteForceCracker, Result
from quas.crypto.ciphers.columnar import ColumnarCipher, ColumnarKey


class ColumnarCracker(BruteForceCracker[ColumnarKey, str]):
    @override
    def cipher(self, key: ColumnarKey) -> ColumnarCipher:
        return ColumnarCipher(key)

    @override
    def keyspace(self) -> Iterator[ColumnarKey]:
        for x in count(2):
            yield ColumnarKey(x)

    @override
    def crack(self, ciphertext: str) -> Iterator[Result[ColumnarKey]]:
        max_cols = len(ciphertext) >> 1
        for key in islice(self.keyspace(), max_cols):
            cipher = self.cipher(key)
            plaintext = cipher.decrypt(ciphertext)
            indices = np.array(english_upper.encode(plaintext), dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            yield Result(key, score)
