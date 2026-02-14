from typing import override

import numpy as np

from quas.crypto.characterizer import Characterizer


class IndexOfCoincidence(Characterizer):
    @override
    def score(self, indices: np.ndarray[tuple[int], np.dtype[np.uint32]]) -> float:
        frequencies = np.bincount(indices, minlength=len(self.ALPHABET))
        ioc = np.sum(frequencies * (frequencies - 1), dtype=float)
        ioc /= indices.size * (indices.size - 1)
        return ioc
