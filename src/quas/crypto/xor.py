import heapq
from collections.abc import Generator
from itertools import cycle
from sys import stdin
from typing import NamedTuple

import click
import numpy as np
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as alphabet
from quas.crypto.characterizer import Characterizer
from quas.crypto.quadgram import quadgram


class Result(NamedTuple):
    key: bytes
    score: float


class XorCipher:
    ALPHABET: Alphabet = alphabet
    CHARACTERIZER: Characterizer = quadgram

    @classmethod
    def crack(cls, ciphertext: bytes) -> Generator[Result]:
        for x in range(0x100):
            key = bytes([x])
            plaintext = cls(key).decrypt(ciphertext)
            plaintext = plaintext.decode(errors="ignore").upper()
            plaintext = np.array(cls.ALPHABET.encode(plaintext), dtype=np.uint32)
            score = cls.CHARACTERIZER.score(plaintext)
            score *= plaintext.size / len(ciphertext)
            yield Result(key, score)

    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(plaintext, cycle(self.key)))

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.encrypt(ciphertext)


@click.command(help="Crack XOR cipher using frequency analysis")
@click.pass_obj
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
@click.argument("ciphertext", type=str, required=False)
def crack(ctx: ContextObject, top: int, ciphertext: str | None) -> None:
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext else stdin.read().strip()
    ciphertext: bytes = bytes.fromhex(ciphertext)

    results = XorCipher.crack(ciphertext)

    table = Table("Key (Hex)", "Plaintext (Bytes)", "Score", box=None)
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = XorCipher(key)
        plaintext = cipher.decrypt(ciphertext).strip()
        table.add_row(key.hex(), str(plaintext), str(score))
    console.print(table, markup=False)
