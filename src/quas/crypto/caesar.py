import heapq
from dataclasses import dataclass

from quas.analysis import english_upper
from quas.crypto.ciphers import CaesarCipher
from quas.crypto.crackers import CaesarCracker


@dataclass
class CaesarCrackResult:
    shift: int
    plaintext: str
    score: float


def perform_caesar_crack(ciphertext: str, top: int) -> list[CaesarCrackResult]:
    cindices = english_upper.encode(ciphertext.upper())
    results = CaesarCracker().crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = CaesarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(CaesarCrackResult(key.value, plaintext, score))
    return top_results
