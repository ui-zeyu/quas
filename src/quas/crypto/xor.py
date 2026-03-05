import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.core.protocols import CommandResult
from quas.crypto.ciphers import XorCipher
from quas.crypto.crackers import XorCracker


@dataclass
class XorCrackItem:
    key_hex: str
    plaintext: bytes
    score: float


@dataclass
class XorPayload:
    items: Sequence[XorCrackItem]


@dataclass
class XorResult(CommandResult[XorPayload]):
    data: XorPayload

    def __rich__(self) -> Table:
        table = Table("Key (Hex)", "Plaintext (Bytes)", "Score", box=None)
        for res in self.data.items:
            table.add_row(res.key_hex, str(res.plaintext), str(res.score))
        return table


def perform_xor_crack(ciphertext_hex: str, top: int) -> XorResult:
    ciphertext_bytes = bytes.fromhex(ciphertext_hex)
    results = XorCracker().crack(ciphertext_bytes)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = XorCipher(key)
        plaintext = cipher.decrypt(ciphertext_bytes)
        top_results.append(XorCrackItem(key.value.hex(), plaintext, score))
    return XorResult(XorPayload(top_results))
