from pathlib import Path
from typing import cast

import click
import numpy as np
import soundfile as sf

from quas.context import ContextObject


def freqs_and_magnitude(y: np.ndarray, sr: float) -> tuple[np.ndarray, np.ndarray]:
    fft = np.fft.rfft(y)
    freqs = np.fft.rfftfreq(len(y), 1 / sr)
    magnitude = np.abs(fft)
    return freqs, magnitude


@click.command()
@click.pass_obj
@click.option("-t", "--top", default=10, help="Top N frequencies")
@click.argument("infile", type=Path)
def frequency(ctx: ContextObject, infile: Path, top: int) -> None:
    console = ctx["console"]

    y, sr = cast(tuple[np.ndarray, int], sf.read(infile))
    y = y.mean(axis=1) if y.ndim > 1 else y

    console.print(f"Sample rate: {sr} Hz")
    console.print(f"Audio length: {len(y)} samples")
    console.print(f"Duration: {len(y) / sr:.2f} seconds")

    freqs, magnitude = freqs_and_magnitude(y, sr)

    peak_indices = np.argsort(magnitude)[-top:]
    peak_freqs = np.sort(freqs[peak_indices]).astype(int)[::-1]
    peak_magnitudes = magnitude[peak_indices]

    console.print(f"\nTop {top} frequencies:")
    for i, (freq, mag) in enumerate(zip(peak_freqs, peak_magnitudes, strict=True)):
        console.print(f"{i}. Frequency: {freq} Hz, Magnitude: {mag:.2e}")
