import heapq
import string
from collections import UserList
from collections.abc import Iterable
from random import Random
from sys import stdin
from typing import NamedTuple, Self

import click
import numpy as np
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import EnglishUpper, english_upper


class Result(NamedTuple):
    key: Key
    score: float


class Key(UserList):
    @classmethod
    def from_palphabet(cls, palphabet: Alphabet) -> Self:
        return cls(palphabet.encoding.values())

    def swap(self, x: int, y: int) -> None:
        self.data[x], self.data[y] = self.data[y], self.data[x]

    def shuffle(self, rng: Random) -> Key:
        key = self.copy()
        rng.shuffle(key)
        return Key(key)


class SubstitutionCipher:
    def __init__(self, key: Key) -> None:
        self.key: Key = key

    def encrypt(self, plaintext: Iterable[int]) -> tuple[int, ...]:
        return tuple(map(self.key.index, plaintext))

    def decrypt(self, ciphertext: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(map(lambda x: self.key[x], ciphertext))

    def decrypt_str(
        self,
        ciphertext: str,
        calphabet: Alphabet,
        palphabet: Alphabet,
    ) -> str:
        plaintext = ""
        for c in ciphertext:
            if x := calphabet.encode_letter(c):
                cc = palphabet.decode_letter(self.key[x])
            else:
                cc = c
            plaintext += cc
        return plaintext


class HillClimber:
    def __init__(
        self,
        quadgram: EnglishUpper,
        restarts: int = 5,
        seed: int | None = None,
    ) -> None:
        self.quadgram = quadgram
        self.restarts = restarts
        self.rng = Random(seed)

    def climb(self, key: Key, ciphertext: tuple[int, ...]) -> Result:
        cipher = SubstitutionCipher(key.shuffle(self.rng))
        plaintext = np.array(cipher.decrypt(ciphertext), dtype=np.uint32)
        best_score = self.quadgram.score_indics(plaintext)

        swaps = np.triu_indices(len(key), k=1)
        while True:
            better = False
            for i, j in zip(*swaps, strict=True):
                mask_i, mask_j = (
                    plaintext == cipher.key[i],
                    plaintext == cipher.key[j],
                )
                plaintext[mask_i], plaintext[mask_j] = cipher.key[j], cipher.key[i]
                cipher.key.swap(i, j)

                score = self.quadgram.score_indics(plaintext)
                if score > best_score:
                    best_score = score
                    better = True
                else:
                    cipher.key.swap(i, j)
                    plaintext[mask_i], plaintext[mask_j] = cipher.key[i], cipher.key[j]
            if not better:
                break
        return Result(cipher.key, best_score)

    def crack(self, key: Key, ciphertext: tuple[int, ...], top: int) -> list[Result]:
        results: list[Result] = []
        for _ in range(self.restarts):
            result = self.climb(key, ciphertext)
            results.append(result)
        return heapq.nlargest(top, results, key=lambda x: x.score)


@click.command()
@click.pass_obj
@click.option("-c", "--calphabet", type=str, default=string.ascii_uppercase)
@click.option("-r", "--restarts", type=int, default=100)
@click.option("-t", "--top", type=int, default=3)
@click.argument("ciphertext", type=str, required=False)
def crack(
    ctx: ContextObject,
    calphabet: str,
    restarts: int,
    top: int,
    ciphertext: str | None,
) -> None:
    console = ctx["console"]

    calphabet: list[str] = calphabet.split() if " " in calphabet else list(calphabet)
    calphabet: Alphabet = Alphabet(calphabet)
    key = Key.from_palphabet(palphabet)

    ciphertext = ciphertext if ciphertext else stdin.read()
    cindics = calphabet.encode(ciphertext)

    climber = HillClimber(english_upper, restarts)
    results = climber.crack(key, cindics, top)

    table = Table("Key", "Plaintext", "Score", box=None, highlight=True)
    for key, score in results:
        cipher = SubstitutionCipher(key)
        plaintext = cipher.decrypt_str(ciphertext, calphabet, palphabet)
        table.add_row(str(key), plaintext, str(score))
    console.print(table)
