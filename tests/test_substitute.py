import string

import numpy as np
from click.testing import CliRunner
from rich.console import Console

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import quadgram
from quas.crypto.substitute import (
    HillClimber,
    Key,
    Result,
    SubstitutionCipher,
)
from quas.crypto.substitute import (
    crack as substitute_command,
)


def test_key_from_palphabet():
    key = Key.from_palphabet(palphabet)
    assert len(key) == 26
    assert all(isinstance(x, int) for x in key.data)


def test_key_shuffle():
    from random import Random

    key1 = Key.from_palphabet(palphabet)
    key2 = key1.shuffle(Random(42))
    key3 = key1.shuffle(Random(42))
    key4 = key1.shuffle(Random(43))

    assert not np.array_equal(key1.data, key2.data)
    assert np.array_equal(key2.data, key3.data)
    assert not np.array_equal(key2.data, key4.data)


def test_key_swap():
    key = Key.from_palphabet(palphabet)
    original_mapping = key.data.copy()

    key.swap(0, 1)
    assert key.data[0] == original_mapping[1]
    assert key.data[1] == original_mapping[0]
    assert np.array_equal(key.data[2:], original_mapping[2:])

    key.swap(0, 1)
    assert np.array_equal(key.data, original_mapping)


def test_substitution_cipher_identity():
    key = Key.from_palphabet(palphabet)
    cipher = SubstitutionCipher(key)
    alphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "HELLO"
    cindices = alphabet.encode(ciphertext)
    pindices = cipher.decrypt(cindices)
    plaintext = alphabet.decode(pindices)

    assert plaintext == ciphertext


def test_substitution_cipher_decrypt_str():
    key = Key.from_palphabet(palphabet)
    cipher = SubstitutionCipher(key)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "HELLO, WORLD!"
    plaintext = cipher.decrypt_str(ciphertext, calphabet, palphabet)

    assert plaintext == ciphertext


def test_result():
    key = Key.from_palphabet(palphabet)
    result = Result(key=key, score=-123.45)

    assert result.key == key
    assert result.score == -123.45


def test_hill_climber_simple_cipher():
    key = Key.from_palphabet(palphabet)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP OEBJA SBK"
    cindices = calphabet.encode(ciphertext)

    climber = HillClimber(quadgram, restarts=3, seed=42)
    result = climber.climb(key, cindices)

    assert result.score > 1
    assert isinstance(result.key, Key)


def test_hill_climber_with_seed():
    key = Key.from_palphabet(palphabet)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindices = calphabet.encode(ciphertext)

    climber1 = HillClimber(quadgram, restarts=3, seed=42)
    result1 = climber1.climb(key, cindices)

    climber2 = HillClimber(quadgram, restarts=3, seed=42)
    result2 = climber2.climb(key, cindices)

    assert np.array_equal(result1.key.data, result2.key.data)
    assert result1.score == result2.score


def test_hill_climber_crack():
    key = Key.from_palphabet(palphabet)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindices = calphabet.encode(ciphertext)

    climber = HillClimber(quadgram, restarts=2, seed=42)
    results = list(climber.crack(key, cindices))

    assert len(results) == 2
    assert all(isinstance(r, Result) for r in results)
    assert all(isinstance(r.key, Key) for r in results)


def test_substitute_command():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(
        substitute_command, ["--restarts", "2", "GUR DHPVP"], obj=ctx_obj
    )
    assert result.exit_code == 0
    assert "Key" in result.output
    assert "Plaintext" in result.output
    assert "Score" in result.output
