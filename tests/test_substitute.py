from unittest.mock import Mock

import pytest

from quas.analysis.alphabet import Alphabet
from quas.commands import SubUseCase as substitute_command
from quas.core.context import ContextObject
from quas.crypto.base import Result
from quas.crypto.ciphers.substitute import SubstituteKey, SubstitutionCipher
from quas.crypto.crackers.substitute import SubstituteCracker


@pytest.fixture
def ctx():
    mock_typer_ctx = Mock()
    mock_typer_ctx.obj = ContextObject(console=Mock(), debug=False)
    return mock_typer_ctx


def test_substitute_crack():
    alphabet = Alphabet(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    cracker = SubstituteCracker(alphabet, restarts=1)
    plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    key = SubstituteKey(alphabet.encode("QWERTYUIOPASDFGHJKLZXCVBNM"))
    cipher = SubstitutionCipher(alphabet, key)
    ciphertext = cipher.decrypt_str(plaintext)
    cindices = alphabet.encode(ciphertext)

    results = list(cracker.crack(cindices))
    assert len(results) >= 1

    for res in results:
        assert isinstance(res, Result)
        assert len(res.key) == len(alphabet)


def test_cli_integration(monkeypatch, ctx):
    alphabet = Alphabet(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    mock_key = SubstituteKey(alphabet.encode("A" * 26))
    mock_crack = Mock(return_value=[Result(mock_key, -100.0)])
    monkeypatch.setattr(SubstituteCracker, "crack", mock_crack)

    substitute_command(
        ctx=ctx,
        ciphertext="test",
        calphabet="A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
        restarts=1,
        top=10,
    )
