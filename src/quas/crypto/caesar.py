import heapq
from collections.abc import Generator
from sys import stdin
from typing import NamedTuple

import click
import numpy as np
from rich.table import Table

from quas.analysis import Alphabet, Characterizer, quadgram
from quas.analysis import english_upper as palphabet
from quas.context import ContextObject


class Result(NamedTuple):
    shift: int
    score: float


class CaesarCipher:
    MOD: int = 26
    ALPHABET: Alphabet = palphabet
    CHARACTERIZER: Characterizer = quadgram

    @classmethod
    def crack(cls, ciphertext: tuple[int, ...]) -> Generator[Result]:
        for shift in range(cls.MOD):
            cipher = cls(shift)
            plaintext = np.array(cipher.decrypt(ciphertext), dtype=np.uint32)
            score = cls.CHARACTERIZER.score(plaintext)
            yield Result(shift, score)

    def __init__(self, shift: int) -> None:
        self.shift = shift

    def decrypt_letter(self, letter: int) -> int:
        return (letter - self.shift) % self.MOD

    def decrypt(self, ciphertext: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(self.decrypt_letter(x) for x in ciphertext)

    def decrypt_str(self, ciphertext: str) -> str:
        plaintext = []
        for c in ciphertext:
            is_lower = c.islower()
            x = self.ALPHABET.encode_letter(c.upper())
            if x is not None:
                cc = self.ALPHABET.decode_letter(self.decrypt_letter(x))
                cc = cc.lower() if is_lower else cc
            else:
                cc = c
            plaintext.append(cc)
        return "".join(plaintext)


@click.command(help="Bruteforce caesar cipher with quadgram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def crack(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext else stdin.read()
    ciphertext = ciphertext.strip().upper()
    cindices = CaesarCipher.ALPHABET.encode(ciphertext)
    results = CaesarCipher.crack(cindices)

    table = Table("Shift", "Plaintext", "Score", box=None)
    for shift, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = CaesarCipher(shift)
        plaintext = cipher.decrypt_str(ciphertext)
        table.add_row(str(shift), plaintext, str(score))
    console.print(table)
