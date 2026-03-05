from dataclasses import dataclass

import numpy as np
from rich.console import Group
from rich.text import Text

from quas.audio.base import AudioSignal, Pipeline
from quas.core.protocols import CommandResult


@dataclass
class FreqItem:
    freq: int
    magnitude: float


@dataclass
class FreqPayload:
    sample_rate: int
    top: int
    items: list[FreqItem]


@dataclass
class FreqResult(CommandResult[FreqPayload]):
    data: FreqPayload

    def __rich__(self) -> Group:
        lines = [
            Text(f"Sample rate: {self.data.sample_rate} Hz"),
            Text(f"Top {self.data.top} frequencies:"),
        ]
        for i, item in enumerate(self.data.items):
            lines.append(
                Text(f"{i}. Frequency: {item.freq} Hz, Magnitude: {item.magnitude:.2e}")
            )
        return Group(*lines)


def frequency_analyzer(top: int) -> Pipeline[AudioSignal, FreqResult]:
    def analyze(sig: AudioSignal) -> FreqResult:
        y, sr = sig.y, sig.sr
        fft = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        magnitude = np.abs(fft)

        peak_indices = np.argsort(magnitude)[-top:]
        peak_freqs = np.sort(freqs[peak_indices]).astype(int)[::-1]
        peak_magnitudes = magnitude[peak_indices]

        items = [
            FreqItem(freq=freq, magnitude=mag)
            for freq, mag in zip(peak_freqs, peak_magnitudes, strict=True)
        ]

        return FreqResult(FreqPayload(sample_rate=sr, top=top, items=items))

    return Pipeline(analyze)
