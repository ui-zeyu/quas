from typing import override

from quas.crypto.base import Key, SubstituteCipher


class AffineKey(Key):
    def __init__(self, a: int, b: int) -> None:
        self.a = a
        self.b = b


class AffineCipher(SubstituteCipher):
    MOD_INVERSES: dict[int, int] = {
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

    def __init__(self, key: AffineKey) -> None:
        self.key = key
        self.a_inv = self.MOD_INVERSES[self.key.a]

    @override
    def decrypt_letter(self, x: int) -> int:
        return (self.a_inv * (x - self.key.b)) % 26
