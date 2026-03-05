from collections.abc import Iterator, Sequence
from typing import NamedTuple, Protocol, override

import numpy as np

from quas.analysis import Alphabet, Evaluator, english_upper, quadgram


class Key: ...


class Result[K: Key](NamedTuple):
    key: K
    score: float


class Cipher[CT](Protocol):
    def decrypt(self, ciphertext: CT) -> CT: ...


class ByteCipher(Cipher[bytes]):
    def decrypt_str(self, ciphertext: bytes) -> str:
        return self.decrypt(ciphertext).decode()


class SubstituteCipher(Cipher[Sequence[int]], Protocol):
    def decrypt_letter(self, x: int) -> int: ...

    def calphabet(self) -> Alphabet:
        return english_upper

    def palphabet(self) -> Alphabet:
        return english_upper

    @override
    def decrypt(self, ciphertext: Sequence[int]) -> Sequence[int]:
        return tuple(self.decrypt_letter(x) for x in ciphertext)


class SingleSubstituteCipher(SubstituteCipher):
    def decrypt_str(self, ciphertext: str) -> str:
        plaintext = []
        for c in ciphertext:
            is_lower = c.islower()
            x = self.calphabet().encode_letter(c.upper())
            if x is not None:
                cc = self.palphabet().decode_letter(self.decrypt_letter(x))
                cc = cc.lower() if is_lower else cc
            else:
                cc = c
            plaintext.append(cc)
        return "".join(plaintext)


class MultiSubstituteCipher(SubstituteCipher):
    def decrypt_str(self, ciphertext: str) -> str:
        return self.calphabet().pattern.sub(
            lambda m: (
                self.palphabet().decode_letter(self.decrypt_letter(x))
                if (x := self.calphabet().encode_letter(m.group()))
                else m.group()
            ),
            ciphertext,
        )


class ShiftCipher(Cipher[str]):
    def decrypt_str(self, ciphertext: str) -> str:
        return "".join(self.decrypt(ciphertext))


class Cracker[K: Key, CT](Protocol):
    CHARACTERIZER: Evaluator = quadgram

    def crack(self, ciphertext: CT) -> Iterator[Result[K]]: ...


class BruteForceCracker[K: Key, CT](Cracker[K, CT], Protocol):
    def cipher(self, key: K) -> Cipher[CT]: ...

    def keyspace(self) -> Iterator[K]: ...

    @override
    def crack(self, ciphertext: CT) -> Iterator[Result[K]]:
        for key in self.keyspace():
            cipher = self.cipher(key)
            plaintext = cipher.decrypt(ciphertext)
            indices = np.array(plaintext, dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            yield Result(key, score)
