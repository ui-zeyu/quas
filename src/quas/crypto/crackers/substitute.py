from collections.abc import Generator
from random import Random
from typing import override

import numpy as np

from quas.analysis import Alphabet
from quas.crypto.base import Cracker, Result
from quas.crypto.ciphers.substitute import SubstituteKey, SubstitutionCipher


class SubstituteCracker(Cracker):
    def __init__(
        self,
        calphabet: Alphabet,
        restarts: int = 5,
        seed: int | None = None,
    ) -> None:
        self.calphabet = calphabet
        self.restarts = restarts
        self._rng = Random(seed)

    def climb(self, ciphertext: tuple[int, ...]) -> Result:
        key = SubstituteKey.random(self._rng)
        cipher = SubstitutionCipher(self.calphabet, key)
        plaintext = np.array(cipher.decrypt(ciphertext), dtype=np.uint32)
        best_score = self.CHARACTERIZER.score(plaintext)

        swaps = np.triu_indices(len(key), k=1)
        while True:
            better = False
            for i, j in zip(*swaps, strict=True):
                mask_i, mask_j = (plaintext == key[i], plaintext == key[j])
                plaintext[mask_i], plaintext[mask_j] = key[j], key[i]
                key.swap(i, j)

                score = self.CHARACTERIZER.score(plaintext)
                if score > best_score:
                    best_score = score
                    better = True
                else:
                    key.swap(i, j)
                    plaintext[mask_i], plaintext[mask_j] = key[i], key[j]
            if not better:
                break
        return Result(key, best_score)

    @override
    def crack(self, ciphertext: tuple[int, ...]) -> Generator[Result]:
        return (self.climb(ciphertext) for _ in range(self.restarts))
