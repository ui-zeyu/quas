from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from typing import NamedTuple, override

import numpy as np

from quas.analysis import Alphabet, Characterizer, english_upper, quadgram


class Key: ...


class Result[K: Key](NamedTuple):
    key: K
    score: float


class Cipher[CT](ABC):
    @abstractmethod
    def decrypt(self, ciphertext: CT) -> CT:
        raise NotImplementedError


class ByteCipher(Cipher[bytes]):
    def decrypt_str(self, ciphertext: bytes) -> str:
        return self.decrypt(ciphertext).decode()


class SubstituteCipher(Cipher[Sequence[int]]):
    @abstractmethod
    def decrypt_letter(self, x: int) -> int:
        raise NotImplementedError

    def calphabet(self) -> Alphabet:
        return english_upper

    def palphabet(self) -> Alphabet:
        return english_upper

    @override
    def decrypt(self, ciphertext: Sequence[int]) -> Sequence[int]:
        return tuple(self.decrypt_letter(x) for x in ciphertext)

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


class ShiftCipher(Cipher[Sequence[str]]):
    @abstractmethod
    def decrypt_str(self, ciphertext: str) -> str:
        ciphertext: Sequence[str] = tuple(ciphertext)
        return "".join(self.decrypt(ciphertext))


class Cracker[K: Key, CT](ABC):
    CHARACTERIZER: Characterizer = quadgram

    @abstractmethod
    def crack(self, ciphertext: CT) -> Generator[Result[K]]:
        raise NotImplementedError


class BruteForceCracker[K: Key, CT](Cracker[K, CT]):
    @abstractmethod
    def cipher(self, key: K) -> Cipher[CT]:
        raise NotImplementedError

    @abstractmethod
    def keyspace(self) -> Generator[K]:
        raise NotImplementedError

    @override
    def crack(self, ciphertext: CT) -> Generator[Result[K]]:
        for key in self.keyspace():
            cipher = self.cipher(key)
            plaintext = cipher.decrypt(ciphertext)
            indices = np.array(plaintext, dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            yield Result(key, score)
