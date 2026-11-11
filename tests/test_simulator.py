"""Physical-frequency regression checks for the signal simulator."""

import numpy as np
from scipy.signal import butter, hilbert, sosfilt

from src.simulator import FS_HZ, expected_fault_frequency, fault_frequencies, simulate_signal


def _envelope_peak(signal: np.ndarray, fs: int, expected_hz: float) -> float:
    band = sosfilt(butter(4, [2000, 4000], btype="bandpass", fs=fs, output="sos"), signal)
    envelope = np.abs(hilbert(band))
    spectrum = np.abs(np.fft.rfft(envelope - envelope.mean()))
    bins = np.fft.rfftfreq(len(envelope), 1 / fs)
    search = (bins >= expected_hz * 0.88) & (bins <= expected_hz * 1.12)
    return float(bins[search][np.argmax(spectrum[search])])


def test_6205_fault_frequency_formulas() -> None:
    values = fault_frequencies(1800)
    assert values.bpfo == pytest.approx(107.55, abs=0.2)
    assert values.bpfi == pytest.approx(162.45, abs=0.2)
    assert values.bsf == pytest.approx(70.75, abs=0.2)
    assert values.ftf == pytest.approx(11.95, abs=0.2)


def test_envelope_spectrum_tracks_defect_frequency() -> None:
    rng = np.random.default_rng(42)
    rpm = 1800.0
    duration_seconds = 5
    for fault in ("Inner Race", "Outer Race", "Ball"):
        expected = expected_fault_frequency(fault, rpm)
        assert expected is not None
        signal = simulate_signal(fault, rpm=rpm, load=1.0, severity=0.9,
                                 snr_db=18, n_samples=FS_HZ * duration_seconds, rng=rng)
        measured = _envelope_peak(signal, FS_HZ, expected)
        assert abs(measured - expected) < expected * 0.025


import pytest