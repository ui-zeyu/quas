from typing import Protocol, runtime_checkable

import numpy as np

from quas.analysis.alphabet import Alphabet, english_upper


@runtime_checkable
class Evaluator(Protocol):
    ALPHABET: Alphabet = english_upper

    def score(self, indices: np.ndarray[tuple[int], np.dtype[np.uint32]]) -> float: ...

    def score_text(self, text: str) -> float:
        indices = self.ALPHABET.encode(text)
        indices = np.array(indices, dtype=np.uint32)
        return self.score(indices)
