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
        self.floor: float = log10(0.01 / total)
        self.offset: float = -self.floor + 1

    def score(self, chars: str) -> float:
        total = 0
        for x in toolz.sliding_window(4, filter(self.ALPHABET.__contains__, chars)):
            total += self.chars_to_score.get("".join(x), self.floor)
        return total


class EnglishUpper(Quadgram):
    ALPHABET = palphabet

    def __init__(self, filepath: Path) -> None:
        super().__init__(filepath)

        self.indics_to_scores: np.ndarray[tuple[int], np.dtype[np.float32]] = np.full(
            2**20,
            self.floor,
            dtype=np.float32,
        )
        for key, score in self.chars_to_score.items():
            indices = cast(tuple[int, int, int, int], self.ALPHABET.encode(key))
            idx = (
                (indices[0] << 0)
                | (indices[1] << 5)
                | (indices[2] << 10)
                | (indices[3] << 15)
            )
            self.indics_to_scores[idx] = score

    def score_indics(
        self,
        indices: np.ndarray[tuple[int], np.dtype[np.uint32]],
    ) -> float:
        if indices.size < 4:
            score = self.floor
        else:
            windows = (
                indices[:-3]
                | indices[1:-2] << 5
                | indices[2:-1] << 10
                | indices[3:] << 15
            )
            score = np.sum(self.indics_to_scores[windows], dtype=float) / indices.size
        return score + self.offset

    @override
    def score(self, chars: str) -> float:
        indices = self.ALPHABET.encode(chars)
        indices = np.array(indices, dtype=np.uint32)
        return self.score_indics(indices)


filepath = Path(__file__).parent / "english_quadgrams.txt"
english_upper = EnglishUpper(filepath)
