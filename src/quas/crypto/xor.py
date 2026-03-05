import heapq
from dataclasses import dataclass

from quas.crypto.ciphers import XorCipher
from quas.crypto.crackers import XorCracker


@dataclass
class XorCrackResult:
    key_hex: str
    plaintext: bytes
    score: float


def perform_xor_crack(ciphertext_hex: str, top: int) -> list[XorCrackResult]:
    ciphertext_bytes = bytes.fromhex(ciphertext_hex)
    results = XorCracker().crack(ciphertext_bytes)

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = XorCipher(key)
        plaintext = cipher.decrypt(ciphertext_bytes)
        top_results.append(XorCrackResult(key.value.hex(), plaintext, score))
    return top_results
