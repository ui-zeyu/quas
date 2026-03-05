import numpy as np

from quas.audio.base import AudioSignal, Pipeline


def frequency_analyzer() -> Pipeline[AudioSignal, tuple[np.ndarray, np.ndarray]]:
    def analyze(sig: AudioSignal) -> tuple[np.ndarray, np.ndarray]:
        y, sr = sig.y, sig.sr
        fft = np.fft.rfft(y)
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        magnitude = np.abs(fft)
        return freqs, magnitude

    return Pipeline(analyze)
