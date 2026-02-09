import heapq
from collections.abc import Generator
from sys import stdin
from typing import NamedTuple

import click
import numpy as np
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import EnglishUpper, english_upper


class Result(NamedTuple):
    a: int
    b: int
    score: float


class Key(NamedTuple):
    a: int
    b: int


class AffineCipher:
    MOD: int = 26
    ALPHABET: Alphabet = palphabet
    QUADGRAM: EnglishUpper = english_upper
    MOD_INVERSES: dict[int, int] = {
        1: 1,
        3: 9,
        5: 21,
        7: 15,
        9: 3,
        11: 19,
        15: 7,
        17: 23,
        19: 11,
        21: 5,
        23: 17,
        25: 25,
    }

    @classmethod
    def crack(cls, ciphertext: tuple[int, ...]) -> Generator[Result]:
        for a in cls.MOD_INVERSES:
            for b in range(cls.MOD):
                cipher = cls(Key(a, b))
                plaintext = np.array(cipher.decrypt(ciphertext), dtype=np.uint32)
                score = cls.QUADGRAM.score_indics(plaintext)
                yield Result(a, b, score)

    def __init__(self, key: Key) -> None:
        self.a, self.b = key.a, key.b
        self.a_inv = self.MOD_INVERSES[self.a]

    def decrypt_letter(self, letter: int) -> int:
        return (self.a_inv * (letter - self.b)) % self.MOD

    def decrypt(self, ciphertext: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(self.decrypt_letter(x) for x in ciphertext)

    def decrypt_str(self, ciphertext: str) -> str:
        plaintext = ""
        for c in ciphertext:
            x = self.ALPHABET.encode_letter(c)
            cc = (
                self.ALPHABET.decode_letter(self.decrypt_letter(x))
                if x is not None
                else c
            )
            plaintext += cc
        return plaintext


@click.command(help="Bruteforce affine cipher with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def bruteforce(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext else stdin.read()
    ciphertext = ciphertext.strip().upper()
    cindics = AffineCipher.ALPHABET.encode(ciphertext)
    results = AffineCipher.crack(cindics)

    table = Table("a", "b", "Plaintext", "Score", box=None)
    for a, b, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = AffineCipher(Key(a, b))
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(a), str(b), plaintext, str(score))
    console.print(table)
