import heapq
import string
from collections import UserList
from collections.abc import Generator, Iterable
from random import Random
from sys import stdin
from typing import NamedTuple, Self

import click
import numpy as np
from rich.table import Table

from quas.analysis.alphabet import Alphabet
from quas.analysis.alphabet import english_upper as palphabet
from quas.analysis.characterizer import Characterizer
from quas.analysis.quadgram import quadgram
from quas.context import ContextObject


class Result(NamedTuple):
    key: Key
    score: float

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key


class Key(UserList):
    @classmethod
    def from_palphabet(cls, palphabet: Alphabet) -> Self:
        return cls(palphabet.encoding.values())

    def __hash__(self):
        return hash(tuple(self.data))

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

    def decrypt(self, ciphertext: Iterable[int]) -> tuple[int, ...]:
        return tuple(map(lambda x: self.key[x], ciphertext))

    def decrypt_str(
        self,
        ciphertext: str,
        calphabet: Alphabet,
        palphabet: Alphabet,
    ) -> str:
        plaintext = []
        for c in ciphertext:
            x = calphabet.encode_letter(c)
            cc = palphabet.decode_letter(self.key[x]) if x is not None else c
            plaintext.append(cc)
        return "".join(plaintext)


class HillClimber:
    def __init__(
        self,
        characterizer: Characterizer,
        restarts: int = 5,
        seed: int | None = None,
    ) -> None:
        self.characterizer = characterizer
        self.restarts = restarts
        self.rng = Random(seed)

    def climb(self, key: Key, ciphertext: tuple[int, ...]) -> Result:
        cipher = SubstitutionCipher(key.shuffle(self.rng))
        plaintext = np.array(cipher.decrypt(ciphertext), dtype=np.uint32)
        best_score = self.characterizer.score(plaintext)

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

                score = self.characterizer.score(plaintext)
                if score > best_score:
                    best_score = score
                    better = True
                else:
                    cipher.key.swap(i, j)
                    plaintext[mask_i], plaintext[mask_j] = cipher.key[i], cipher.key[j]
            if not better:
                break
        return Result(cipher.key, best_score)

    def crack(self, key: Key, ciphertext: tuple[int, ...]) -> Generator[Result]:
        for _ in range(self.restarts):
            yield self.climb(key, ciphertext)


@click.command(help="Crack substitution cipher using hill climbing with N-gram scoring")
@click.pass_obj
@click.option(
    "-c",
    "--calphabet",
    type=str,
    default=string.ascii_uppercase,
    help="Cipher alphabet (default: A-Z)",
)
@click.option(
    "-r",
    "--restarts",
    type=int,
    default=100,
    help="Number of hill climbing restarts",
)
@click.option("-t", "--top", type=int, default=3, help="Show top N results")
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
    ciphertext = ciphertext.upper()
    cindices = calphabet.encode(ciphertext)

    climber = HillClimber(quadgram, restarts)
    results = climber.crack(key, cindices)

    table = Table("Key", "Plaintext", "Score", box=None)
    for key, score in heapq.nlargest(top, set(results), lambda x: x.score):
        cipher = SubstitutionCipher(key)
        plaintext = cipher.decrypt_str(ciphertext, calphabet, palphabet)
        table.add_row(palphabet.decode(key), plaintext, str(score))
    console.print(table)
