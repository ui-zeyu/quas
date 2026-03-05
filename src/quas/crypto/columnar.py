import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.core.protocols import CommandResult
from quas.crypto.ciphers import ColumnarCipher
from quas.crypto.crackers import ColumnarCracker


@dataclass
class ColumnarCrackItem:
    cols: int
    plaintext: str
    score: float


@dataclass
class ColumnarPayload:
    items: Sequence[ColumnarCrackItem]


@dataclass
class ColumnarResult(CommandResult[ColumnarPayload]):
    data: ColumnarPayload

    def __rich__(self) -> Table:
        table = Table("Cols", "Plaintext", "Score", box=None)
        for res in self.data.items:
            table.add_row(str(res.cols), res.plaintext, str(res.score))
        return table


def perform_columnar_crack(ciphertext: str, top: int) -> ColumnarResult:
    results = ColumnarCracker().crack(ciphertext.upper())

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = ColumnarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(ColumnarCrackItem(key.cols, plaintext, score))
    return ColumnarResult(ColumnarPayload(top_results))
