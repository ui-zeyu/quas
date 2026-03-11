import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.crypto.ciphers import RailFenceCipher
from quas.crypto.crackers import RailFenceCracker


@dataclass
class RailFenceCrackItem:
    rails: int
    plaintext: str
    score: float


@dataclass
class RailFencePayload:
    items: Sequence[RailFenceCrackItem]

    def __rich__(self) -> Table:
        table = Table("Rails", "Plaintext", "Score", box=None)
        for res in self.items:
            table.add_row(str(res.rails), res.plaintext, str(res.score))
        return table


def perform_railfence_crack(ciphertext: str, top: int) -> RailFencePayload:
    results = RailFenceCracker().crack(ciphertext.upper())

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = RailFenceCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(RailFenceCrackItem(key.rails, plaintext, score))
    return RailFencePayload(top_results)
