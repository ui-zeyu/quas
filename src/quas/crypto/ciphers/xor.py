from itertools import cycle
from typing import override

from quas.crypto.base import ByteCipher, Key


class XorKey(Key):
    def __init__(self, value: bytes) -> None:
        self.value = value


class XorCipher(ByteCipher):
    def __init__(self, key: XorKey) -> None:
        self.key = key

    @override
    def decrypt(self, ciphertext: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(ciphertext, cycle(self.key.value)))
