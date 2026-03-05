from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

from quas.behinder.aes import Mode
from quas.behinder.aes import decrypt as decrypt_aes
from quas.behinder.base import derive_behinder_key
from quas.behinder.xor import decrypt as decrypt_xor


def test_behinder_aes_ecb():
    password = b"rebeyond"
    key = derive_behinder_key(password)
    plaintext = b"hello world"
    cipher = AES.new(key, AES.MODE_ECB)
    ct = cipher.encrypt(pad(plaintext, AES.block_size))

    # decrypt_aes expects bytes
    payload = decrypt_aes(ct, [password], mode=Mode.ECB)
    assert payload is not None
    assert payload.plaintext == "hello world"
    assert payload.password == password


def test_behinder_aes_cbc():
    password = b"rebeyond"
    key = derive_behinder_key(password)
    plaintext = b"hello world"
    iv = b"\x00" * 16
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad(plaintext, AES.block_size))

    payload = decrypt_aes(ct, [password], mode=Mode.CBC)
    assert payload is not None
    assert payload.plaintext == "hello world"
    assert payload.password == password


def test_behinder_xor():
    password = b"rebeyond"
    key = derive_behinder_key(password)
    xor_key = key[1:] + key[:1]
    plaintext = b"hello world"

    from itertools import cycle

    ct = bytes(x ^ y for x, y in zip(plaintext, cycle(xor_key), strict=False))

    payload = decrypt_xor(ct, [password])
    assert payload is not None
    assert payload.plaintext == "hello world"
    assert payload.password == password


def test_behinder_aes_wrong_password():
    password = b"rebeyond"
    wrong_password = b"wrong"
    key = derive_behinder_key(password)
    plaintext = b"hello world"
    cipher = AES.new(key, AES.MODE_ECB)
    ct = cipher.encrypt(pad(plaintext, AES.block_size))

    payload = decrypt_aes(ct, [wrong_password], mode=Mode.ECB)
    assert payload is None
