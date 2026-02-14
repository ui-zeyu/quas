from abc import ABC, abstractmethod

import numpy as np

from quas.crypto.alphabet import Alphabet, english_upper


class Characterizer(ABC):
    ALPHABET: Alphabet = english_upper

    @abstractmethod
    def score(self, indices: np.ndarray[tuple[int], np.dtype[np.uint32]]) -> float:
        raise NotImplementedError

    def score_text(self, text: str) -> float:
        indices = self.ALPHABET.encode(text)
        indices = np.array(indices, dtype=np.uint32)
        return self.score(indices)
