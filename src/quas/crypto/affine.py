import heapq
from collections.abc import Generator
from sys import stdin
from typing import NamedTuple

import click
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import english_upper


class Result(NamedTuple):
    a: int
    b: int
    plaintext: str
    score: float


class AffineCipher:
    MOD = 26
    ALPHABET = palphabet
    MOD_INVERSES = {
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

    def decrypt_letter(self, c: str, a_inv: int, b: int) -> str:
        if x := self.ALPHABET.encode_letter(c):
            y = (a_inv * (x - b)) % self.MOD
            return self.ALPHABET.decode_letter(y)
        else:
            return c

    def decrypt(self, ciphertext: str, a_inv: int, b: int) -> str:
        return "".join(self.decrypt_letter(x, a_inv, b) for x in ciphertext)

    def bruteforce(self, ciphertext: str) -> Generator[Result]:
        ciphertext = ciphertext.strip().upper()
        for a in self.MOD_INVERSES:
            a_inv = self.MOD_INVERSES[a]
            for b in range(self.MOD):
                plaintext = self.decrypt(ciphertext, a_inv, b)
                score = english_upper.score(plaintext)
                yield Result(a, b, plaintext, score)


@click.command(help="Bruteforce affine cipher with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def bruteforce(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext else stdin.read()
    cipher = AffineCipher()
    results = cipher.bruteforce(ciphertext)

    table = Table("a", "b", "Plaintext", "Score", box=None, highlight=True)
    for x in heapq.nlargest(top, results, lambda x: x.score):
        table.add_row(str(x.a), str(x.b), x.plaintext, f"{x.score}")
    console.print(table)
