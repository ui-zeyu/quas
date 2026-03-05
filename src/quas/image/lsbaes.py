from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from pathlib import Path
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import toolz
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from PIL import Image
from rich.console import Console


class DecryptResult(NamedTuple):
    password: str
    plaintext: str


PADDING_SIZE: int = 32


def entropy(data: np.ndarray[tuple[int], np.dtype[np.uint8]]) -> float:
    x, counts = np.unique(data, return_counts=True)
    probs = counts / len(data)
    return -np.sum(probs * np.log2(probs))


def extract_lsb_bits(image: Path) -> np.ndarray[tuple[int], np.dtype[np.uint8]]:
    img = Image.open(image).convert("RGBA")
    rgb = np.array(img, dtype=np.uint8)[:, :, :3]
    return (rgb & 1).ravel()


def unpack_iv_ct(
    console: Console,
    bytes: np.ndarray[tuple[int], np.dtype[np.uint8]],
) -> tuple[bytes, bytes]:
    len_ct_bytes, bytes = bytes[:4], bytes[4:]
    len_ct = int.from_bytes(len_ct_bytes.tobytes(), "little")
    console.print(f"[bold]Ciphertext length:[/bold] {len_ct}")
    assert len_ct % AES.block_size == 0

    iv, ct = bytes[: AES.block_size], bytes[AES.block_size : len_ct]
    return iv.tobytes(), ct.tobytes()


def analyse(bits: np.ndarray[tuple[int], np.dtype[np.uint8]]) -> None:
    chunks = bits.reshape(-1, 128, 3)
    mean = np.mean(chunks, axis=1)

    r_channel = mean[:, 0]
    g_channel = mean[:, 1]
    b_channel = mean[:, 2]
    x = range(len(mean))

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    axes[0].plot(x, r_channel, "r-", linewidth=2)
    axes[0].set_ylabel("Mean Value")
    axes[0].set_title("R Channel")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(x, g_channel, "g-", linewidth=2)
    axes[1].set_ylabel("Mean Value")
    axes[1].set_title("G Channel")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(x, b_channel, "b-", linewidth=2)
    axes[2].set_xlabel("Block Index")
    axes[2].set_ylabel("Mean Value")
    axes[2].set_title("B Channel")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def decrypt_batch(
    passwords: Sequence[bytes],
    iv: bytes,
    ct: bytes,
) -> DecryptResult | None:
    for password in passwords:
        key = sha256(password).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        try:
            pt = unpad(cipher.decrypt(ct), block_size=PADDING_SIZE)
            return DecryptResult(password.decode(), pt.decode())
        except ValueError:
            continue
    return None


def crack(
    iv: bytes,
    ct: bytes,
    wordlist: Path,
    num_worker: int,
) -> DecryptResult | None:
    passwords = wordlist.read_bytes().splitlines()
    chunks = toolz.partition_all(num_worker, passwords)

    with ProcessPoolExecutor(num_worker) as executor:
        futures = [executor.submit(decrypt_batch, chunk, iv, ct) for chunk in chunks]
        for future in as_completed(futures):
            if result := future.result():
                return result
    return None


# Logic for LSB-AES extraction.
