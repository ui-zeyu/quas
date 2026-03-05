import heapq
from dataclasses import dataclass

from rich.table import Table

from quas.analysis import english_upper
from quas.core.protocols import CommandResult
from quas.crypto.ciphers import CaesarCipher
from quas.crypto.crackers import CaesarCracker


@dataclass
class CaesarCrackItem:
    shift: int
    plaintext: str
    score: float


@dataclass
class CaesarPayload:
    items: list[CaesarCrackItem]


@dataclass
class CaesarResult(CommandResult[CaesarPayload]):
    data: CaesarPayload

    def __rich__(self) -> Table:
        table = Table("Shift", "Plaintext", "Score", box=None)
        for res in self.data.items:
            table.add_row(str(res.shift), res.plaintext, str(res.score))
        return table


def perform_caesar_crack(ciphertext: str, top: int) -> CaesarResult:
    cindices = english_upper.encode(ciphertext.upper())
    results = CaesarCracker().crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = CaesarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(CaesarCrackItem(key.value, plaintext, score))
    return CaesarResult(CaesarPayload(top_results))
