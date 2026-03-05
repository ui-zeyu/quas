from math import log10
from pathlib import Path
from typing import cast, override

import numpy as np

from quas.analysis.evaluator import Evaluator


class Quadgram(Evaluator):
    def __init__(self, filepath: Path) -> None:
        ngrams: dict[str, int] = {}
        for line in filepath.read_text().splitlines():
            key, count = line.split(maxsplit=1)
            ngrams[key] = int(count)
        total = sum(ngrams.values())

        self.char_to_score: dict[str, float] = {}
        for key, count in ngrams.items():
            self.char_to_score[key] = log10(count / total)
        self.floor: float = log10(0.01 / total)
        self.offset: float = -self.floor + 1

        self.idx_to_score: np.ndarray[tuple[int], np.dtype[np.float32]] = np.full(
            2**20,
            self.floor,
            dtype=np.float32,
        )
        for key, score in self.char_to_score.items():
            indices = cast(tuple[int, int, int, int], self.ALPHABET.encode(key))
            idx = (
                (indices[0] << 0)
                | (indices[1] << 5)
                | (indices[2] << 10)
                | (indices[3] << 15)
            )
            self.idx_to_score[idx] = score

    @override
    def score(self, indices: np.ndarray[tuple[int], np.dtype[np.uint32]]) -> float:
        if indices.size < 4:
            score = self.floor
        else:
            windows = (
                indices[:-3]
                | indices[1:-2] << 5
                | indices[2:-1] << 10
                | indices[3:] << 15
            )
            score = np.sum(self.idx_to_score[windows], dtype=float) / indices.size
        return score + self.offset


filepath = Path(__file__).parent / "english_quadgrams.txt"
quadgram = Quadgram(filepath)
