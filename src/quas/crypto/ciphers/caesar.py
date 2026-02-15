from typing import override

from quas.crypto.base import Key, SubstituteCipher


class CaesarKey(Key):
    def __init__(self, value: int) -> None:
        self.value = value % 26


class CaesarCipher(SubstituteCipher):
    def __init__(self, key: CaesarKey) -> None:
        self.key = key

    @override
    def decrypt_letter(self, x: int) -> int:
        return (x - self.key.value) % 26
