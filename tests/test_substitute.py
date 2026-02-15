import string

import numpy as np
from click.testing import CliRunner
from rich.console import Console

from quas.analysis.alphabet import Alphabet
from quas.context import ContextObject
from quas.crypto.base import Result
from quas.crypto.ciphers.substitute import (
    SubstituteKey,
    SubstitutionCipher,
)
from quas.crypto.crackers import SubstituteCracker
from quas.crypto.substitute import crack as substitute_command


def test_substitute_key_random():
    from random import Random

    key1 = SubstituteKey.random(Random(42))
    assert len(key1) == 26
    assert all(isinstance(x, int) for x in key1.data)


def test_substitute_key_swap():
    from random import Random

    key = SubstituteKey.random(Random(42))
    original_mapping = key.data.copy()

    key.swap(0, 1)
    assert key.data[0] == original_mapping[1]
    assert key.data[1] == original_mapping[0]
    assert np.array_equal(key.data[2:], original_mapping[2:])

    key.swap(0, 1)
    assert np.array_equal(key.data, original_mapping)


def test_substitution_cipher_identity():
    key = SubstituteKey(range(26))
    alphabet = Alphabet(list(string.ascii_uppercase))
    cipher = SubstitutionCipher(alphabet, key)

    ciphertext = "HELLO"
    cindices = alphabet.encode(ciphertext)
    pindices = cipher.decrypt(cindices)
    plaintext = alphabet.decode(pindices)

    assert plaintext == ciphertext


def test_substitution_cipher_decrypt_str():
    key = SubstituteKey(range(26))
    alphabet = Alphabet(list(string.ascii_uppercase))
    cipher = SubstitutionCipher(alphabet, key)

    ciphertext = "HELLO, WORLD!"
    plaintext = cipher.decrypt_str(ciphertext)

    assert plaintext == ciphertext


def test_result():
    from random import Random

    key = SubstituteKey.random(Random(42))
    result = Result(key=key, score=-123.45)

    assert result.key == key
    assert result.score == -123.45


def test_hill_climber_simple_cipher():
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP OEBJA SBK"
    cindices = calphabet.encode(ciphertext)

    climber = SubstituteCracker(calphabet, restarts=3, seed=42)
    result = climber.climb(cindices)

    assert result.score > 1
    assert isinstance(result.key, SubstituteKey)


def test_hill_climber_with_seed():
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindices = calphabet.encode(ciphertext)

    climber1 = SubstituteCracker(calphabet, restarts=3, seed=42)
    result1 = climber1.climb(cindices)

    climber2 = SubstituteCracker(calphabet, restarts=3, seed=42)
    result2 = climber2.climb(cindices)

    assert np.array_equal(result1.key.data, result2.key.data)
    assert result1.score == result2.score


def test_hill_climber_crack():
    calphabet = Alphabet(list(string.ascii_uppercase))

    ciphertext = "GUR DHPVP"
    cindices = calphabet.encode(ciphertext)

    climber = SubstituteCracker(calphabet, restarts=2, seed=42)
    results = list(climber.crack(cindices))

    assert len(results) == 2
    assert all(isinstance(r.key, SubstituteKey) for r in results)


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
