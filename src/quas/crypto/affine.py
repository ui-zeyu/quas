import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.analysis import english_upper
from quas.crypto.ciphers import AffineCipher
from quas.crypto.crackers import AffineCracker


@dataclass
class AffineCrackItem:
    a: int
    b: int
    plaintext: str
    score: float


@dataclass
class AffinePayload:
    items: Sequence[AffineCrackItem]

    def __rich__(self) -> Table:
        table = Table("a", "b", "Plaintext", "Score", box=None)
        for res in self.items:
            table.add_row(str(res.a), str(res.b), res.plaintext, str(res.score))
        return table


def perform_affine_crack(ciphertext: str, top: int) -> AffinePayload:
    cindices = english_upper.encode(ciphertext.upper())
    results = AffineCracker().crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = AffineCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(AffineCrackItem(key.a, key.b, plaintext, score))
    return AffinePayload(top_results)
