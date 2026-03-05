import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from rich.table import Table

from quas.analysis.alphabet import Alphabet
from quas.core.protocols import CommandResult
from quas.crypto.ciphers import SubstitutionCipher
from quas.crypto.crackers import SubstituteCracker


@dataclass
class SubCrackItem:
    key: str
    plaintext: str
    score: float


@dataclass
class SubPayload:
    items: Sequence[SubCrackItem]


@dataclass
class SubResult(CommandResult[SubPayload]):
    data: SubPayload

    def __rich__(self) -> Table:
        table = Table("Key", "Plaintext", "Score", box=None)
        for res in self.data.items:
            table.add_row(res.key, res.plaintext, str(res.score))
        return table


def perform_sub_crack(
    ciphertext: str, calphabet: str, restarts: int, top: int
) -> SubResult:
    calphabet_list = calphabet.split() if " " in calphabet else list(calphabet)
    alphabet_obj = Alphabet(calphabet_list)
    ciphertext_upper = ciphertext.upper()
    cindices = alphabet_obj.encode(ciphertext_upper)

    results = SubstituteCracker(alphabet_obj, restarts=restarts).crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = SubstitutionCipher(alphabet_obj, key)
        plaintext = cipher.decrypt_str(ciphertext_upper)
        top_results.append(
            SubCrackItem(cipher.palphabet().decode(key), plaintext, score)
        )
    return SubResult(SubPayload(top_results))
