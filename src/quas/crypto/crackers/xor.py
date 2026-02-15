from collections.abc import Generator
from typing import override

import numpy as np

from quas.analysis import english_upper
from quas.crypto.base import BruteForceCracker, Result
from quas.crypto.ciphers.xor import XorCipher, XorKey


class XorCracker(BruteForceCracker[XorKey, bytes]):
    @override
    def cipher(self, key: XorKey) -> XorCipher:
        raise NotImplementedError

    @override
    def keyspace(self) -> Generator[XorKey]:
        return (XorKey(bytes([x])) for x in range(256))

    @override
    def crack(self, ciphertext: bytes) -> Generator[Result[XorKey]]:
        for key in self.keyspace():
            cipher = XorCipher(key)
            plaintext = cipher.decrypt(ciphertext)
            text = plaintext.decode(errors="ignore").upper()
            indices = np.array(english_upper.encode(text), dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            score *= indices.size / len(ciphertext)
            yield Result(key, score)
