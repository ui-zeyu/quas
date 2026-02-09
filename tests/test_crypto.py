from click.testing import CliRunner
from rich.console import Console

from quas.context import ContextObject
from quas.crypto.affine import (
    AffineCipher,
    Key,
)
from quas.crypto.affine import (
    bruteforce as affine_command,
)
from quas.crypto.quadgram import Quadgram, english_upper


def test_mod_inverses():
    assert AffineCipher.MOD == 26
    assert AffineCipher.MOD_INVERSES[1] == 1
    assert AffineCipher.MOD_INVERSES[3] == 9
    assert AffineCipher.MOD_INVERSES[5] == 21
    assert AffineCipher.MOD_INVERSES[7] == 15
    assert AffineCipher.MOD_INVERSES[9] == 3
    assert AffineCipher.MOD_INVERSES[11] == 19
    assert AffineCipher.MOD_INVERSES[15] == 7
    assert AffineCipher.MOD_INVERSES[17] == 23
    assert AffineCipher.MOD_INVERSES[19] == 11
    assert AffineCipher.MOD_INVERSES[21] == 5
    assert AffineCipher.MOD_INVERSES[23] == 17
    assert AffineCipher.MOD_INVERSES[25] == 25


def test_load_quadgrams():
    assert isinstance(english_upper, Quadgram)
    assert isinstance(english_upper.chars_to_score, dict)
    assert len(english_upper.chars_to_score) > 0
    assert isinstance(english_upper.floor, float)
    assert english_upper.floor < 0


def test_score_quadgrams_english():
    text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    score = english_upper.score(text)
    assert isinstance(score, float)
    assert score < 0


def test_score_quadgrams_random():
    text = "XYZQKDLFMNVBCRPUGZWYHS"
    score = english_upper.score(text)
    assert isinstance(score, float)
    assert score < 0


def test_decrypt_affine_identity():
    ciphertext = "HELLO"
    a = 1
    b = 0
    cipher = AffineCipher(Key(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == ciphertext


def test_decrypt_affine_shift():
    ciphertext = "KHOOR"
    a = 1
    b = 3
    cipher = AffineCipher(Key(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO"


def test_affine_command():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(affine_command, ["HELLO"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "a" in result.output
    assert "b" in result.output
    assert "Plaintext" in result.output


def test_affine_command_with_top():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(affine_command, ["--top", "5", "HELLO"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "Score" in result.output


def test_affine_command_preserves_non_alpha():
    ciphertext = "HELLO, WORLD!"
    a = 1
    b = 0
    cipher = AffineCipher(Key(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == ciphertext
    assert "," in plaintext
    assert " " in plaintext
    assert "!" in plaintext


def test_affine_command_case_insensitive():
    ciphertext = "HELLO"
    a = 1
    b = 0
    cipher = AffineCipher(Key(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO"
