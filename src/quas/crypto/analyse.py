from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from quas.analysis import english_upper
from quas.analysis.ioc import IndexOfCoincidence
from quas.analysis.quadgram import quadgram


@dataclass
class FrequencyStat:
    char: str
    count: int
    percent: float
    binary: str
    standard_percent: float | None = None


@dataclass
class AnalysePayload:
    total_length: int
    frequencies: Sequence[FrequencyStat]
    alpha_frequencies: Sequence[FrequencyStat]
    ioc_score: float
    quadgram_score: float
    alpha_length: int

    def __rich__(self) -> Group:
        group_items = []

        table1 = Table("Char", "Count", "Percent", "Binary", box=None, expand=True)
        for stat in self.frequencies:
            table1.add_row(
                stat.char, str(stat.count), f"{stat.percent:.2f}%", stat.binary
            )
        group_items.append(Panel(table1, title="Frequency Analysis"))

        table2 = Table("Char", "Count", "Percent", "Standard", box=None, expand=True)
        for stat in self.alpha_frequencies:
            standard_str = (
                f"{stat.standard_percent:.2f}%"
                if stat.standard_percent is not None
                else "0.00%"
            )
            table2.add_row(
                stat.char, str(stat.count), f"{stat.percent:.2f}%", standard_str
            )
        group_items.append(Panel(table2, title="Frequency Analysis (Upper Case)"))

        table3 = Table(
            "Scorer", "Score", "Length", "Normal Range", box=None, expand=True
        )
        table3.add_row(
            "IoC",
            f"{self.ioc_score:.3f}",
            str(self.alpha_length),
            "0.0567 - 0.0767",
        )
        table3.add_row(
            "Quadgram",
            f"{self.quadgram_score:.3f}",
            str(self.alpha_length),
            "10.0 - 11.0",
        )
        group_items.append(Panel(table3, title="Scoring Analysis"))

        return Group(*group_items)


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


def perform_analysis(ciphertext: str) -> AnalysePayload:
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

    return AnalysePayload(
        total_length=total_length,
        frequencies=frequencies,
        alpha_frequencies=alpha_frequencies,
        ioc_score=score_ioc,
        quadgram_score=score_quadgram,
        alpha_length=alpha_length,
    )
