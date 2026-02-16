from typing import override

import numpy as np

from quas.crypto.base import Key, ShiftCipher


class ColumnarKey(Key):
    def __init__(self, cols: int) -> None:
        self.cols = cols


class ColumnarCipher(ShiftCipher):
    def __init__(self, key: ColumnarKey) -> None:
        self.key = key

    @override
    def decrypt(self, ciphertext: str) -> str:
        rows = (len(ciphertext) + self.key.cols - 1) // self.key.cols
        remainder = len(ciphertext) % self.key.cols or self.key.cols

        mask = np.zeros((rows, self.key.cols), dtype=bool)
        mask[:-1, :] = True
        mask[-1, :remainder] = True

        grid = np.empty((rows, self.key.cols), dtype=np.str_)
        grid.T[mask.T] = tuple(ciphertext)
        return "".join(grid[mask])
