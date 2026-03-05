from pathlib import Path

import click
import numpy as np

from quas.audio.base import AudioSignal, Pipeline, select_channel
from quas.context import ContextObject


def frequency_analyzer() -> Pipeline[AudioSignal, tuple[np.ndarray, np.ndarray]]:
    def analyze(sig: AudioSignal) -> tuple[np.ndarray, np.ndarray]:
        y, sr = sig.y, sig.sr
        fft = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        magnitude = np.abs(fft)
        return freqs, magnitude

    return Pipeline(analyze)


@click.command()
@click.pass_obj
@click.option("-t", "--top", default=10, help="Top N frequencies")
@click.option("-c", "--channel", type=int, help="Channel to use")
@click.option("--dtype", default="float64", help="Audio data type")
@click.argument("infile", type=Path)
def frequency(
    ctx: ContextObject, infile: Path, top: int, channel: int | None, dtype: str
) -> None:
    console = ctx["console"]
    sig = AudioSignal.read(infile, dtype=dtype)

    pipeline = select_channel(channel) | frequency_analyzer()
    freqs, magnitude = pipeline(sig)

    peak_indices = np.argsort(magnitude)[-top:]
    peak_freqs = np.sort(freqs[peak_indices]).astype(int)[::-1]
    peak_magnitudes = magnitude[peak_indices]

    console.print(f"Sample rate: {sig.sr} Hz")
    console.print(f"Top {top} frequencies:")
    for i, (freq, mag) in enumerate(zip(peak_freqs, peak_magnitudes, strict=True)):
        console.print(f"{i}. Frequency: {freq} Hz, Magnitude: {mag:.2e}")
