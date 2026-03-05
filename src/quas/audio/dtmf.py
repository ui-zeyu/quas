from dataclasses import dataclass
from itertools import groupby
from typing import override

import numpy as np
from rich.text import Text
from scipy.signal import spectrogram

from quas.audio.base import Analyzer, AudioSignal
from quas.core.protocols import CommandResult


@dataclass
class DTMFPayload:
    digits: str


@dataclass
class DTMFResult(CommandResult[DTMFPayload]):
    data: DTMFPayload

    def __rich__(self) -> Text:
        return Text(f"DTMF digits: {self.data.digits}")


class DTMFRecognizer(Analyzer[AudioSignal, DTMFResult]):
    LOW_FREQS = np.array((697, 770, 852, 941))
    HIGH_FREQS = np.array((1209, 1336, 1477, 1633))
    DTMF_MAP = {
        (697, 1209): "1",
        (697, 1336): "2",
        (697, 1477): "3",
        (697, 1633): "A",
        (770, 1209): "4",
        (770, 1336): "5",
        (770, 1477): "6",
        (770, 1633): "B",
        (852, 1209): "7",
        (852, 1336): "8",
        (852, 1477): "9",
        (852, 1633): "C",
        (941, 1209): "*",
        (941, 1336): "0",
        (941, 1477): "#",
        (941, 1633): "D",
    }

    def __init__(self, tolerance: int = 20, window_ms: int = 40):
        self.tolerance = tolerance
        self.window_ms = window_ms

    @override
    def __call__(self, data: AudioSignal) -> DTMFResult:
        y, sr = data.y, data.sr
        nperseg = int(sr * (self.window_ms / 1000))
        f, _, sxx = spectrogram(y, sr, nperseg=nperseg, noverlap=0)

        l_mask, h_mask = (f > 0) & (f <= 1050), (f >= 1100) & (f <= 2000)
        p_l = f[l_mask][np.argmax(sxx[l_mask, :], axis=0)]
        p_h = f[h_mask][np.argmax(sxx[h_mask, :], axis=0)]

        d_l = np.abs(p_l[:, None] - self.LOW_FREQS)
        d_h = np.abs(p_h[:, None] - self.HIGH_FREQS)
        n_l, n_h = np.argmin(d_l, axis=1), np.argmin(d_h, axis=1)

        valid = (np.min(d_l, axis=1) < self.tolerance) & (
            np.min(d_h, axis=1) < self.tolerance
        )

        seq = [
            self.DTMF_MAP.get((self.LOW_FREQS[n_l[i]], self.HIGH_FREQS[n_h[i]]))
            if valid[i]
            else None
            for i in range(sxx.shape[1])
        ]
        digits = "".join(k for k, _ in groupby(seq) if k is not None)
        return DTMFResult(DTMFPayload(digits=digits))

    @classmethod
    def perform(
        cls,
        sig: AudioSignal,
        tolerance: int,
        window_ms: int,
        channel: int | None,
    ) -> DTMFResult:
        from quas.audio.base import select_channel

        pipeline = select_channel(channel) | cls(
            tolerance=tolerance, window_ms=window_ms
        )
        return pipeline(sig)
