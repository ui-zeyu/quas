import heapq
from dataclasses import dataclass

from quas.analysis import english_upper
from quas.crypto.ciphers import AffineCipher
from quas.crypto.crackers import AffineCracker


@dataclass
class AffineCrackResult:
    a: int
    b: int
    plaintext: str
    score: float


def perform_affine_crack(ciphertext: str, top: int) -> list[AffineCrackResult]:
    cindices = english_upper.encode(ciphertext.upper())
    results = AffineCracker().crack(cindices)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = AffineCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(AffineCrackResult(key.a, key.b, plaintext, score))
    return top_results
