from click.testing import CliRunner
from rich.console import Console

from quas.analysis.alphabet import english_upper
from quas.analysis.quadgram import Quadgram, quadgram
from quas.context import ContextObject
from quas.crypto.affine import crack as affine_command
from quas.crypto.caesar import crack as caesar_command
from quas.crypto.ciphers.affine import AffineCipher, AffineKey
from quas.crypto.ciphers.caesar import CaesarCipher, CaesarKey
from quas.crypto.crackers import CaesarCracker


def test_mod_inverses():
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
    assert isinstance(quadgram, Quadgram)
    assert isinstance(quadgram.char_to_score, dict)
    assert len(quadgram.char_to_score) > 0
    assert isinstance(quadgram.floor, float)
    assert quadgram.floor < 0


def test_score_quadgrams_english():
    text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    score = quadgram.score_text(text)
    assert isinstance(score, float)
    assert score > 1


def test_score_quadgrams_random():
    text = "XYZQKDLFMNVBCRPUGZWYHS"
    score = quadgram.score_text(text)
    assert isinstance(score, float)
    assert score > 1


def test_decrypt_affine_identity():
    ciphertext = "HELLO"
    a = 1
    b = 0
    cipher = AffineCipher(AffineKey(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == ciphertext


def test_decrypt_affine_shift():
    ciphertext = "KHOOR"
    a = 1
    b = 3
    cipher = AffineCipher(AffineKey(a, b))
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
    cipher = AffineCipher(AffineKey(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == ciphertext
    assert "," in plaintext
    assert " " in plaintext
    assert "!" in plaintext


def test_affine_command_case_insensitive():
    ciphertext = "HELLO"
    a = 1
    b = 0
    cipher = AffineCipher(AffineKey(a, b))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO"


def test_caesar_decrypt_letter_identity():
    shift = 0
    cipher = CaesarCipher(CaesarKey(shift))
    assert cipher.decrypt_letter(0) == 0
    assert cipher.decrypt_letter(25) == 25


def test_caesar_decrypt_letter_shift():
    shift = 3
    cipher = CaesarCipher(CaesarKey(shift))
    assert cipher.decrypt_letter(3) == 0
    assert cipher.decrypt_letter(4) == 1
    assert cipher.decrypt_letter(7) == 4
    assert cipher.decrypt_letter(0) == 23


def test_caesar_decrypt_identity():
    ciphertext = "HELLO"
    shift = 0
    cipher = CaesarCipher(CaesarKey(shift))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == ciphertext


def test_caesar_decrypt_shift():
    ciphertext = "KHOOR"
    shift = 3
    cipher = CaesarCipher(CaesarKey(shift))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO"


def test_caesar_decrypt_preserves_non_alpha():
    ciphertext = "KHOOR, ZRUOG!"
    shift = 3
    cipher = CaesarCipher(CaesarKey(shift))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO, WORLD!"
    assert "," in plaintext
    assert " " in plaintext
    assert "!" in plaintext


def test_caesar_decrypt_case_preserved():
    ciphertext = "Khoor, Zruog!"
    shift = 3
    cipher = CaesarCipher(CaesarKey(shift))
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "Hello, World!"


def test_caesar_crack():
    ciphertext = "KHOOR ZRUOG"
    cipher_indices = english_upper.encode(ciphertext)
    cracker = CaesarCracker()
    results = list(cracker.crack(cipher_indices))
    assert len(results) == 26
    assert all(isinstance(r.key, CaesarKey) for r in results)
    assert all(0 <= r.key.value < 26 for r in results)
    assert all(isinstance(r.score, float) for r in results)


def test_caesar_crack_find_best():
    ciphertext = "KHOOR ZRUOG"
    cipher_indices = english_upper.encode(ciphertext)
    cracker = CaesarCracker()
    results = list(cracker.crack(cipher_indices))
    best = max(results, key=lambda x: x.score)
    assert best.key.value == 3
    cipher = CaesarCipher(best.key)
    plaintext = cipher.decrypt_str(ciphertext)
    assert plaintext == "HELLO WORLD"


def test_caesar_command():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(caesar_command, ["KHOOR"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "Shift" in result.output
    assert "Plaintext" in result.output


def test_caesar_command_with_top():
    runner = CliRunner()
    ctx_obj: ContextObject = {"console": Console(), "debug": False}
    result = runner.invoke(caesar_command, ["--top", "5", "KHOOR"], obj=ctx_obj)
    assert result.exit_code == 0
    assert "Score" in result.output
