import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.analysis import english_upper
from quas.crypto.ciphers import CaesarCipher
from quas.crypto.crackers import CaesarCracker


@dataclass
class CaesarCrackItem:
    shift: int
    plaintext: str
    score: float


@dataclass
class CaesarPayload:
    items: Sequence[CaesarCrackItem]

    def __rich__(self) -> Table:
        table = Table("Shift", "Plaintext", "Score", box=None)
        for res in self.items:
            table.add_row(str(res.shift), res.plaintext, str(res.score))
        return table


def perform_caesar_crack(ciphertext: str, top: int) -> CaesarPayload:
    cindices = english_upper.encode(ciphertext.upper())
    results = CaesarCracker().crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = CaesarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(CaesarCrackItem(key.value, plaintext, score))
    return CaesarPayload(top_results)
