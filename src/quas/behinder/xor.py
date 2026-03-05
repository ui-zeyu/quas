from collections.abc import Sequence
from itertools import cycle

from .base import BehinderPayload, derive_behinder_key


def decrypt(ciphertext: bytes, passwords: Sequence[bytes]) -> BehinderPayload | None:
    for password in passwords:
        key = derive_behinder_key(password)
        xor_key = key[1:] + key[:1]
        plaintext = bytes(
            x ^ y for x, y in zip(ciphertext, cycle(xor_key), strict=False)
        )

        try:
            decoded = plaintext.decode()
            return BehinderPayload(password=password, key=key, plaintext=decoded)
        except UnicodeDecodeError:
            continue

    return None
