from collections import Counter
from dataclasses import dataclass

import numpy as np

from quas.analysis import english_upper
from quas.analysis.ioc import IndexOfCoincidence
from quas.analysis.quadgram import quadgram

STANDARD_FREQUENCY: dict[str, float] = {
    "E": 12.7,
    "T": 9.1,
    "A": 8.2,
    "O": 7.5,
    "I": 7.0,
    "N": 6.7,
    "S": 6.3,
    "H": 6.1,
    "R": 6.0,
    "D": 4.3,
    "L": 4.0,
    "C": 2.8,
    "U": 2.8,
    "M": 2.4,
    "W": 2.4,
    "F": 2.2,
    "G": 2.0,
    "Y": 2.0,
    "P": 1.9,
    "B": 1.5,
    "V": 1.0,
    "K": 0.8,
    "J": 0.15,
    "X": 0.15,
    "Q": 0.10,
    "Z": 0.07,
}


@dataclass
class FrequencyStat:
    char: str
    count: int
    percent: float
    binary: str
    standard_percent: float | None = None


@dataclass
class AnalysisResult:
    total_length: int
    frequencies: list[FrequencyStat]
    alpha_frequencies: list[FrequencyStat]
    ioc_score: float
    quadgram_score: float
    alpha_length: int


def perform_analysis(ciphertext: str) -> AnalysisResult:
    frequencies = []
    total_length = len(ciphertext)
    if total_length > 0:
        for char, count in Counter(ciphertext).most_common():
            percent = count / total_length * 100
            frequencies.append(
                FrequencyStat(
                    char=char, count=count, percent=percent, binary=f"{ord(char):08b}"
                )
            )

    alpha_text = "".join(x for x in ciphertext if x.isalpha()).upper()
    alpha_length = len(alpha_text)
    alpha_frequencies = []
    if alpha_length > 0:
        for char, count in Counter(alpha_text).most_common():
            percent = count / alpha_length * 100
            standard = STANDARD_FREQUENCY.get(char, 0.0)
            alpha_frequencies.append(
                FrequencyStat(
                    char=char,
                    count=count,
                    percent=percent,
                    binary=f"{ord(char):08b}",
                    standard_percent=standard,
                )
            )

    if alpha_length > 0:
        indices = np.array(english_upper.encode(alpha_text), dtype=np.uint32)
        score_ioc = IndexOfCoincidence().score(indices)
        score_quadgram = quadgram.score(indices)
    else:
        score_ioc = 0.0
        score_quadgram = 0.0

    return AnalysisResult(
        total_length=total_length,
        frequencies=frequencies,
        alpha_frequencies=alpha_frequencies,
        ioc_score=score_ioc,
        quadgram_score=score_quadgram,
        alpha_length=alpha_length,
    )
