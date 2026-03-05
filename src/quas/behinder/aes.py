import enum
from collections.abc import Sequence

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad

from .base import IV, BehinderPayload, derive_behinder_key


class Mode(enum.Enum):
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC


def decrypt(
    ciphertext: bytes,
    passwords: Sequence[bytes],
    mode: Mode,
) -> BehinderPayload | None:
    aes_mode = mode.value

    for password in passwords:
        key = derive_behinder_key(password)
        cipher = (
            AES.new(key, aes_mode)
            if aes_mode == AES.MODE_ECB
            else AES.new(key, aes_mode, iv=IV)
        )

        try:
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size).decode()
            return BehinderPayload(password=password, key=key, plaintext=plaintext)
        except UnicodeDecodeError, ValueError:
            continue

    return None
