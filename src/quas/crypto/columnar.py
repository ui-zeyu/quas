import heapq
from dataclasses import dataclass

from quas.crypto.ciphers import ColumnarCipher
from quas.crypto.crackers import ColumnarCracker


@dataclass
class ColumnarCrackResult:
    cols: int
    plaintext: str
    score: float


def perform_columnar_crack(ciphertext: str, top: int) -> list[ColumnarCrackResult]:
    results = ColumnarCracker().crack(ciphertext.upper())

    top_results = []
    for key, score in heapq.nlargest(top, results, lambda x: x.score):
        cipher = ColumnarCipher(key)
        plaintext = cipher.decrypt_str(ciphertext)
        top_results.append(ColumnarCrackResult(key.cols, plaintext, score))
    return top_results
