from abc import ABC, abstractmethod
from math import log10
from pathlib import Path
from typing import cast, override

import numpy as np
import toolz

from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet


class Quadgram(ABC):
    @property
    @classmethod
    @abstractmethod
    def ALPHABET(cls) -> Alphabet:
        raise NotImplementedError

    def __init__(self, filepath: Path) -> None:
        ngrams: dict[str, int] = {}
        for line in filepath.read_text().splitlines():
            key, count = line.split(maxsplit=1)
            ngrams[key] = int(count)
        total = sum(ngrams.values())

        self.chars_to_score: dict[str, float] = {}
        for key, count in ngrams.items():
            self.chars_to_score[key] = log10(count / total)
        self.floor = log10(0.01 / total)

    def score(self, chars: str) -> float:
        total = 0
        for x in toolz.sliding_window(4, filter(self.ALPHABET.__contains__, chars)):
            total += self.chars_to_score.get("".join(x), self.floor)
        return total


class EnglishUpper(Quadgram):
    ALPHABET = palphabet
    MULTIPLIERS = np.array([1, 26, 676, 17576], dtype=np.uint32)

    def __init__(self, filepath: Path) -> None:
        super().__init__(filepath)

        self.indics_to_scores = np.full(26**4, self.floor, dtype=np.float32)
        for key, score in self.chars_to_score.items():
            indics = cast(tuple[int, int, int, int], self.ALPHABET.encode(key))
            idx = indics @ self.MULTIPLIERS
            self.indics_to_scores[idx] = score

    def score_indics(self, indics: np.ndarray[tuple[int], np.dtype[np.uint8]]) -> float:
        windows = np.lib.stride_tricks.sliding_window_view(indics, 4)
        indices = windows @ self.MULTIPLIERS
        return float(np.sum(self.indics_to_scores[indices]))

    @override
    def score(self, chars: str) -> float:
        indics = self.ALPHABET.encode(chars)
        indics = np.array(indics, dtype=np.uint8)
        return self.score_indics(indics)


filepath = Path(__file__).parent / "english_quadgrams.txt"
english_upper = EnglishUpper(filepath)
