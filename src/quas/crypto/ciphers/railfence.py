from typing import override

import numpy as np

from quas.crypto.base import Key, ShiftCipher


class RailFenceKey(Key):
    def __init__(self, rails: int) -> None:
        self.rails = rails


class RailFenceCipher(ShiftCipher):
    def __init__(self, key: RailFenceKey) -> None:
        self.key = key

    @override
    def decrypt(self, ciphertext: str) -> str:
        ciphertext: np.ndarray = np.array(tuple(ciphertext), dtype=np.str_)

        cycle = 2 * (self.key.rails - 1)
        pos = np.arange(ciphertext.size) % cycle
        pos = np.minimum(pos, cycle - pos)
        rows, cols = pos, np.arange(ciphertext.size)

        cipher_indices = np.lexsort((cols, rows))
        plaintext_indices = np.argsort(cipher_indices)
        plaintext = ciphertext[plaintext_indices]
        return "".join(plaintext)
