import heapq
from dataclasses import dataclass

from quas.crypto.ciphers import RailFenceCipher
from quas.crypto.crackers import RailFenceCracker


@dataclass
class RailFenceCrackResult:
    rails: int
    plaintext: str
    score: float


def perform_railfence_crack(ciphertext: str, top: int) -> list[RailFenceCrackResult]:
    results = RailFenceCracker().crack(ciphertext.upper())

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = RailFenceCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(RailFenceCrackResult(key.rails, plaintext, score))
    return top_results
