import string

import numpy as np
from click.testing import CliRunner
from rich.console import Console

from quas.context import ContextObject
from quas.crypto.alphabet import Alphabet
from quas.crypto.alphabet import english_upper as palphabet
from quas.crypto.quadgram import english_upper
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
    assert key.mapping.dtype == np.uint8


def test_key_shuffle():
    key1 = Key.from_palphabet(palphabet)
    key2 = key1.shuffle(np.random.default_rng(42))
    key3 = key1.shuffle(np.random.default_rng(42))
    key4 = key1.shuffle(np.random.default_rng(43))

    assert not np.array_equal(key1.mapping, key2.mapping)
    assert np.array_equal(key2.mapping, key3.mapping)
    assert not np.array_equal(key2.mapping, key4.mapping)


def test_key_swap():
    key = Key.from_palphabet(palphabet)
    original_mapping = key.mapping.copy()

    key.swap(0, 1)
    assert key.mapping[0] == original_mapping[1]
    assert key.mapping[1] == original_mapping[0]
    assert np.array_equal(key.mapping[2:], original_mapping[2:])

    key.swap(0, 1)
    assert np.array_equal(key.mapping, original_mapping)


def test_substitution_cipher_identity():
    key = Key.from_palphabet(palphabet)
    cipher = SubstitutionCipher(key)
    alphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "HELLO"
    cindics = np.array(alphabet.encode(ciphertext), dtype=np.uint8)
    pindics = cipher.decrypt(cindics)
    plaintext = alphabet.decode(pindics)

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
    cindics = np.array(calphabet.encode(ciphertext), dtype=np.uint8)

    climber = HillClimber(english_upper, restarts=3, seed=42)
    result = climber.climb(key, cindics)

    assert result.score < 0
    assert isinstance(result.key, Key)


def test_hill_climber_with_seed():
    key = Key.from_palphabet(palphabet)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindics = np.array(calphabet.encode(ciphertext), dtype=np.uint8)

    climber1 = HillClimber(english_upper, restarts=3, seed=42)
    result1 = climber1.climb(key, cindics)

    climber2 = HillClimber(english_upper, restarts=3, seed=42)
    result2 = climber2.climb(key, cindics)

    assert np.array_equal(result1.key.mapping, result2.key.mapping)
    assert result1.score == result2.score


def test_hill_climber_crack():
    key = Key.from_palphabet(palphabet)
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindics = np.array(calphabet.encode(ciphertext), dtype=np.uint8)

    climber = HillClimber(english_upper, restarts=2, seed=42)
    results = climber.crack(key, cindics, top=5)

    assert len(results) <= 5
    assert all(isinstance(r, Result) for r in results)
    assert all(isinstance(r.key, Key) for r in results)
    assert results[0].score >= results[-1].score


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
