from itertools import groupby
from typing import override

import numpy as np
from scipy.signal import spectrogram

from quas.audio.base import Analyzer, AudioSignal


class MorseDecoder(Analyzer[AudioSignal, tuple[str, str]]):
    MORSE_MAP = {
        ".-": "A",
        "-...": "B",
        "-.-.": "C",
        "-..": "D",
        ".": "E",
        "..-.": "F",
        "--.": "G",
        "....": "H",
        "..": "I",
        ".---": "J",
        "-.-": "K",
        ".-..": "L",
        "--": "M",
        "-.": "N",
        "---": "O",
        ".--.": "P",
        "--.-": "Q",
        ".-.": "R",
        "...": "S",
        "-": "T",
        "..-": "U",
        "...-": "V",
        ".--": "W",
        "-..-": "X",
        "-.--": "Y",
        "--..": "Z",
        ".----": "1",
        "..---": "2",
        "...--": "3",
        "....-": "4",
        ".....": "5",
        "-....": "6",
        "--...": "7",
        "---..": "8",
        "----.": "9",
        "-----": "0",
        "/": " ",
    }

    def __init__(self, tolerance: int = 20, window_ms: int = 10):
        self.tolerance = tolerance
        self.window_ms = window_ms

    @override
    def __call__(self, data: AudioSignal) -> tuple[str, str]:
        y, sr = data.y, data.sr
        nperseg = int(sr * (self.window_ms / 1000))
        f, _, sxx = spectrogram(y, sr, nperseg=nperseg)

        target = f[np.argmax(np.var(sxx, axis=1))]
        mask = (f >= target - self.tolerance) & (f <= target + self.tolerance)
        energy = np.max(sxx[mask, :], axis=0)
        noise = np.median(sxx[~mask, :], axis=0) + 1e-10

        binary = (energy / noise) > 5.0
        seq = [(val, len(list(grp))) for val, grp in groupby(binary)]
        dot_size = min((length for v, length in seq if v), default=1)

        res = []
        for val, length in seq:
            if val:
                res.append("." if length < dot_size * 2 else "-")
            else:
                if length > dot_size * 5:
                    res.append(" / ")
                elif length > dot_size * 2:
                    res.append(" ")

        morse = "".join(res).strip(" /")
        words = [
            "".join(self.MORSE_MAP.get(c, "?") for c in word.split())
            for word in morse.split("/")
        ]
        text = " ".join(words)
        return morse, text
