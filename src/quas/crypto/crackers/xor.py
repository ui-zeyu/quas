from collections.abc import Generator
from typing import override

import numpy as np

from quas.analysis import english_upper
from quas.crypto.base import ByteCracker, Result
from quas.crypto.ciphers.xor import XorCipher, XorKey


class XorCracker(ByteCracker):
    @override
    def crack(self, ciphertext: bytes) -> Generator[Result[XorKey]]:
        for x in range(0x100):
            key = XorKey(bytes([x]))
            cipher = XorCipher(key)
            plaintext = cipher.decrypt(ciphertext)
            text = plaintext.decode(errors="ignore").upper()
            indices = np.array(english_upper.encode(text), dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            score *= indices.size / len(ciphertext)
            yield Result(key, score)
