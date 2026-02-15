from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import NamedTuple, override

import numpy as np

from quas.analysis import Alphabet, Characterizer, english_upper, quadgram


class Key: ...


class Result[K: Key](NamedTuple):
    key: K
    score: float


class Cipher(ABC):
    def calphabet(self) -> Alphabet:
        return english_upper

    def palphabet(self) -> Alphabet:
        return english_upper

    @abstractmethod
    def decrypt_letter(self, x: int) -> int:
        raise NotImplementedError

    def decrypt(self, ciphertext: tuple[int, ...]) -> tuple[int, ...]:
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


class ByteCipher(ABC):
    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        raise NotImplementedError

    def decrypt_str(self, ciphertext: bytes, encoding: str = "utf-8") -> str:
        return self.decrypt(ciphertext).decode(encoding, errors="replace")


class Cracker(ABC):
    CHARACTERIZER: Characterizer = quadgram

    @abstractmethod
    def crack(self, ciphertext: tuple[int, ...]) -> Generator[Result]:
        raise NotImplementedError


class ByteCracker(ABC):
    CHARACTERIZER: Characterizer = quadgram

    @abstractmethod
    def crack(self, ciphertext: bytes) -> Generator[Result]:
        raise NotImplementedError


class BruteForceCracker[K: Key](Cracker):
    @abstractmethod
    def cipher(self, key: K) -> Cipher:
        raise NotImplementedError

    @abstractmethod
    def keyspace(self) -> Generator[K]:
        raise NotImplementedError

    @override
    def crack(self, ciphertext: tuple[int, ...]) -> Generator[Result[K]]:
        for key in self.keyspace():
            cipher = self.cipher(key)
            plaintext = cipher.decrypt(ciphertext)
            indices = np.array(plaintext, dtype=np.uint32)
            score = self.CHARACTERIZER.score(indices)
            yield Result(key, score)
