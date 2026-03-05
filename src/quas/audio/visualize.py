from typing import override

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from scipy.signal import spectrogram

from quas.audio.base import Analyzer, AudioSignal


class AudioVisualizer(Analyzer[AudioSignal, Figure]):
    def __init__(self, title: str = "Audio Analysis", window_ms: int = 20):
        self.title = title
        self.window_ms = window_ms

    @override
    def __call__(self, data: AudioSignal) -> Figure:
        y, sr = data.y, data.sr
        fig, (ax_wave, ax_spec) = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
        fig.suptitle(self.title, fontsize=14, fontweight="bold")

        time = np.arange(y.size) / sr
        ax_wave.plot(time, y, color="cornflowerblue", linewidth=0.5)
        ax_wave.set_title("Waveform")
        ax_wave.grid(True, alpha=0.3)
        y_max = np.max(np.abs(y)) or 1.0
        ax_wave.set_ylim(-y_max * 1.1, y_max * 1.1)

        nperseg = int(sr * (self.window_ms / 1000))
        f, t, sxx = spectrogram(y, sr, nperseg=nperseg)
        sxx_db = 10 * np.log10(sxx + 1e-10)
        cax = ax_spec.imshow(
            sxx_db,
            aspect="auto",
            origin="lower",
            extent=[t[0], t[-1], f[0], f[-1]],
            cmap="magma",
        )
        ax_spec.set_title("Spectrogram")
        fig.colorbar(cax, ax=ax_spec, format="%+2.0f dB")

        fig.tight_layout()
        return fig
