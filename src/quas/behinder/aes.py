import enum

from Cryptodome.Cipher import AES


class Mode(enum.Enum):
    ECB = AES.MODE_ECB
    CBC = AES.MODE_CBC
