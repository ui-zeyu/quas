import pytest
from click.testing import CliRunner
from quas.base import ContextObject
from rich.console import Console

from quas.crypto.substitute import (
    HillClimber,
    KeyGenerator,
    Result,
    SubstitutionCipher,
)
from quas.crypto.substitute import (
    crack as substitute_command,
)


def test_key_generator_random():
    key_gen = KeyGenerator()
    key1 = key_gen.shuffle()
    assert key_gen.is_valid_key(key1)

    key2 = key_gen.shuffle()
    assert key_gen.is_valid_key(key2)
    assert key1 != key2


def test_key_generator_with_seed():
    key_gen1 = KeyGenerator(seed=42)
    key1 = key_gen1.shuffle()

    key_gen2 = KeyGenerator(seed=42)
    key2 = key_gen2.shuffle()

    assert key1 == key2


def test_key_generator_identity():
    key_gen = KeyGenerator()
    key = key_gen.identity()
    assert key == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    assert key_gen.is_valid_key(key)


def test_key_generator_swap():
    key_gen = KeyGenerator()
    key = key_gen.identity()
    swapped = key_gen.swap_letters(key, 0, 1)
    assert swapped[0] == "B"
    assert swapped[1] == "A"
    assert swapped[2:] == "CDEFGHIJKLMNOPQRSTUVWXYZ"


def test_key_generator_is_valid():
    key_gen = KeyGenerator()
    assert key_gen.is_valid_key("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert key_gen.is_valid_key("BCDEFGHIJKLMNOPQRSTUVWXYZA")
    assert not key_gen.is_valid_key("ABCDEFGHIJKLMNOPQRSTUVWXY")
    assert not key_gen.is_valid_key("ABCDEFGHIJKLMNOPQRSTUVWXYY")
    assert not key_gen.is_valid_key("ABCDEFGHIJKLMNOPQRSTUVWXY!")


def test_substitution_cipher_identity():
    cipher = SubstitutionCipher(key=KeyGenerator().identity())
    assert cipher.decrypt("HELLO") == "HELLO"
    assert cipher.encrypt("HELLO") == "HELLO"


def test_substitution_cipher_preserves_case():
    cipher = SubstitutionCipher(key="BCDEFGHIJKLMNOPQRSTUVWXYZA")
    assert cipher.decrypt("Hello") == "Ifmmp"
    assert cipher.decrypt("HELLO") == "IFMMP"


def test_substitution_cipher_preserves_non_alpha():
    cipher = SubstitutionCipher(key="BCDEFGHIJKLMNOPQRSTUVWXYZA")
    assert cipher.decrypt("HELLO, WORLD!") == "IFMMP, XPSME!"
    assert cipher.decrypt("Hello, World!") == "Ifmmp, Xpsme!"


def test_substitution_cipher_encrypt_decrypt():
    cipher = SubstitutionCipher(key="BCDEFGHIJKLMNOPQRSTUVWXYZA")
    encrypted = cipher.encrypt("HELLO WORLD")
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == "HELLO WORLD"


def test_substitution_cipher_invalid_key():

    with pytest.raises(ValueError):
        SubstitutionCipher(key="INVALID")


def test_result_dataclass():
    result = Result(key="ABC", plaintext="test", score=-123.45)
    assert result.calphabet == "ABC"
    assert result.plaintext == "test"
    assert result.score == -123.45
    result_str = str(result)
    assert "Key: ABC" in result_str
    assert "Plaintext: test" in result_str
    assert "Score: -123.45" in result_str


def test_hill_climber_simple_cipher():
    key_gen = KeyGenerator(seed=42)
    cipher = SubstitutionCipher(key=key_gen.identity())
    encrypted = "GUR DHPVP OEBJA SBK"

    climber = HillClimber(cipher=cipher, iterations=1000, restarts=3, seed=42)
    result = climber.crack(encrypted)

    assert result.score < 0
    assert len(result.plaintext) == len(encrypted)
    assert isinstance(result.calphabet, str)


def test_hill_climber_with_seed():
    ciphertext = "GUR DHPVP OEBJA SBK"

    key_gen1 = KeyGenerator(seed=42)
    cipher1 = SubstitutionCipher(key=key_gen1.identity())
    climber1 = HillClimber(cipher=cipher1, iterations=1000, restarts=3, seed=42)
    result1 = climber1.crack(ciphertext)

    key_gen2 = KeyGenerator(seed=42)
    cipher2 = SubstitutionCipher(key=key_gen2.identity())
    climber2 = HillClimber(cipher=cipher2, iterations=1000, restarts=3, seed=42)
    result2 = climber2.crack(ciphertext)

    assert result1.calphabet == result2.calphabet
    assert result1.plaintext == result2.plaintext
    assert result1.score == result2.score


def test_hill_climber_best_result_property():
    key_gen = KeyGenerator(seed=42)
    cipher = SubstitutionCipher(key=key_gen.identity())
    ciphertext = "GUR DHPVP"

    climber = HillClimber(cipher=cipher, iterations=100, restarts=2, seed=42)
    assert climber.best_result is None

    result = climber.crack(ciphertext)
    assert climber.best_result is not None
    assert climber.best_result == result


def test_substitute_command():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(
        substitute_command,
        ["--iterations", "100", "--restarts", "2", "GUR DHPVP"],
        obj=ctx_obj,
    )
    assert result.exit_code == 0
    assert "Key" in result.output
    assert "Plaintext" in result.output
    assert "Score" in result.output


def test_substitute_command_from_stdin():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(
        substitute_command, ["--iterations", "100", "GUR DHPVP"], obj=ctx_obj
    )
    assert result.exit_code == 0
    assert "Key" in result.output
    assert "Plaintext" in result.output
    assert "Score" in result.output


def test_substitute_command_with_seed():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result1 = runner.invoke(
        substitute_command,
        ["--seed", "42", "--iterations", "100", "GUR DHPVP"],
        obj=ctx_obj,
    )
    assert result1.exit_code == 0

    result2 = runner.invoke(
        substitute_command,
        ["--seed", "42", "--iterations", "100", "GUR DHPVP"],
        obj=ctx_obj,
    )
    assert result2.exit_code == 0
    assert result1.output == result2.output
