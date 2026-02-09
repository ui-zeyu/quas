import heapq
import string
from collections.abc import Iterable
from sys import stdin
from typing import NamedTuple, Self

import click
import numpy as np
from numpy.random import Generator
from rich.table import Table

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import EnglishUpper, english_upper


class Result(NamedTuple):
    key: Key
    score: float


class Key:
    @classmethod
    def from_palphabet(cls, palphabet: Alphabet) -> Self:
        mapping = np.array(tuple(palphabet.encoding.values()), dtype=np.uint8)
        return cls(mapping)

    def __init__(self, mapping: np.ndarray[tuple[int], np.dtype[np.uint8]]) -> None:
        self.mapping: np.ndarray[tuple[int], np.dtype[np.uint8]] = mapping

    def __len__(self) -> int:
        return len(self.mapping)

    def swap(self, x: int, y: int) -> None:
        self.mapping[x], self.mapping[y] = self.mapping[y], self.mapping[x]

    def shuffle(self, rng: Generator) -> Key:
        mapping = self.mapping.copy()
        rng.shuffle(mapping)
        return Key(mapping)


class SubstitutionCipher:
    def __init__(self, key: Key) -> None:
        self.key: Key = key

    def encrypt(self, plaintext: Iterable[int]) -> tuple[int, ...]:
        return tuple(map(lambda x: np.where(self.key.mapping == x)[0][0], plaintext))

    def decrypt(
        self,
        ciphertext: np.ndarray[tuple[int], np.dtype[np.uint8]],
    ) -> np.ndarray[tuple[int], np.dtype[np.uint8]]:
        return self.key.mapping[ciphertext]

    def decrypt_str(
        self,
        ciphertext: str,
        calphabet: Alphabet,
        palphabet: Alphabet,
    ) -> str:
        plaintext = ""
        for c in ciphertext:
            if x := calphabet.encode_letter(c):
                cc = palphabet.decode_letter(self.key.mapping[x])
            else:
                cc = c
            plaintext += cc
        return plaintext


class HillClimber:
    def __init__(
        self,
        quadgram: EnglishUpper,
        iterations: int = 5000,
        restarts: int = 5,
        seed: int | None = None,
    ) -> None:
        self.quadgram = quadgram
        self.iterations = iterations
        self.restarts = restarts
        self.rng = np.random.default_rng(seed)

    def climb(
        self,
        key: Key,
        ciphertext: np.ndarray[tuple[int], np.dtype[np.uint8]],
    ) -> Result:
        cipher = SubstitutionCipher(key.shuffle(self.rng))
        plaintext = cipher.decrypt(ciphertext)
        best_score = self.quadgram.score_indics(plaintext)

        for _ in range(self.iterations):
            best_key = cipher.key
            x, y = self.rng.choice(range(len(key)), 2, replace=False)
            best_key.swap(x, y)
            plaintext = cipher.decrypt(ciphertext)
            score = self.quadgram.score_indics(plaintext)
            if score > best_score:
                best_score = score
            else:
                best_key.swap(x, y)
        return Result(cipher.key, best_score)

    def crack(
        self,
        key: Key,
        ciphertext: np.ndarray[tuple[int], np.dtype[np.uint8]],
        top: int = 10,
    ) -> list[Result]:
        results: list[Result] = []
        for _ in range(self.restarts):
            result = self.climb(key, ciphertext)
            results.append(result)
        return heapq.nlargest(top, results, key=lambda x: x.score)


@click.command()
@click.pass_obj
@click.option("-i", "--iterations", type=int, default=3000)
@click.option("-r", "--restarts", type=int, default=10)
@click.option("-t", "--top", type=int, default=3)
@click.option("-c", "--calphabet", type=str, default=string.ascii_uppercase)
@click.argument("ciphertext", type=str, required=False)
def crack(
    ctx: ContextObject,
    ciphertext: str | None,
    calphabet: str,
    iterations: int,
    restarts: int,
    top: int,
) -> None:
    console = ctx["console"]

    calphabet: list[str] = calphabet.split() if " " in calphabet else list(calphabet)
    calphabet: Alphabet = Alphabet(calphabet)
    key = Key.from_palphabet(palphabet)

    ciphertext = ciphertext if ciphertext else stdin.read()
    cindics = np.array(calphabet.encode(ciphertext), dtype=np.uint8)

    climber = HillClimber(english_upper, iterations, restarts)
    results = climber.crack(key, cindics, top)

    table = Table("Key", "Plaintext", "Score", box=None, highlight=True)
    for key, score in results:
        cipher = SubstitutionCipher(key)
        plaintext = cipher.decrypt_str(ciphertext, calphabet, palphabet)
        table.add_row(str(key), plaintext, str(score))
    console.print(table)
