import heapq
from dataclasses import dataclass

from quas.analysis.alphabet import Alphabet
from quas.crypto.ciphers import SubstitutionCipher
from quas.crypto.crackers import SubstituteCracker


@dataclass
class SubCrackResult:
    key: str
    plaintext: str
    score: float


def perform_sub_crack(
    ciphertext: str, calphabet: str, restarts: int, top: int
) -> list[SubCrackResult]:
    calphabet_list = calphabet.split() if " " in calphabet else list(calphabet)
    alphabet_obj = Alphabet(calphabet_list)
    ciphertext_upper = ciphertext.upper()
    cindices = alphabet_obj.encode(ciphertext_upper)
    results = SubstituteCracker(alphabet_obj, restarts).crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, set(results), lambda x: x.score):
        cipher = SubstitutionCipher(alphabet_obj, key)
        plaintext = cipher.decrypt_str(ciphertext_upper)
        top_results.append(
            SubCrackResult(cipher.palphabet().decode(key), plaintext, score)
        )
    return top_results
