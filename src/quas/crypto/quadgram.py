from math import log10
from pathlib import Path

import toolz


class Quadgram:
    def __init__(self, filepath: Path) -> None:
        ngrams: dict[str, int] = {}
        for line in filepath.read_text().splitlines():
            key, count = line.split(maxsplit=1)
            ngrams[key] = int(count)
        total = sum(ngrams.values())

        self._scores: dict[str, float] = {}
        for key, count in ngrams.items():
            self._scores[key] = log10(count / total)
        self._floor = log10(0.01 / total)

    def score(self, text: str) -> float:
        total = 0
        for x in toolz.sliding_window(4, filter(str.isalpha, text)):
            total += self._scores.get("".join(x), self._floor)
        return total


filepath = Path(__file__).parent / "english_quadgrams.txt"
quadgram = Quadgram(filepath)
