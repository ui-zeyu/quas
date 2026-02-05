import dataclasses
import string
from sys import stdin

import click
from rich.table import Table

from quas.base import ContextObject
from quas.crypto.quadgram import quadgram

MOD = 26
ALPHABET = string.ascii_uppercase
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


@dataclasses.dataclass
class Result:
    a: int
    b: int
    plaintext: str
    score: float


def decrypt(ciphertext: str, a_inv: int, b: int) -> str:
    plaintext = ""
    for c in ciphertext:
        if c.isalpha():
            x = ALPHABET.index(c)
            y = (a_inv * (x - b)) % MOD
            plaintext += ALPHABET[y]
        else:
            plaintext += c
    return plaintext


@click.command(help="Bruteforce affine cipher with N-gram scoring")
@click.pass_obj
@click.argument("ciphertext", type=str, required=False)
@click.option("-t", "--top", type=int, default=10, help="Show top N results")
def bruteforce(ctx: ContextObject, ciphertext: str | None, top: int) -> None:
    console = ctx["console"]

    ciphertext = ciphertext if ciphertext else stdin.read()
    ciphertext = ciphertext.strip().upper()

    results = []
    for a in MOD_INVERSES:
        a_inv = MOD_INVERSES[a]
        for b in range(MOD):
            plaintext = decrypt(ciphertext, a_inv, b)
            score = quadgram.score(plaintext)
            results.append(Result(a, b, plaintext, score))
    results.sort(key=lambda x: x.score, reverse=True)

    table = Table("a", "b", "Plaintext", "Score", box=None, highlight=True)
    for x in results[:top]:
        table.add_row(str(x.a), str(x.b), x.plaintext, f"{x.score}")
    console.print(table)
