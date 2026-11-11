"""Time, frequency, and envelope-spectrum feature extraction."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, hilbert, sosfilt
from scipy.stats import kurtosis, skew

from src.simulator import FS_HZ, fault_frequencies

ROOT = Path(__file__).resolve().parents[1]


def extract_features(signal: np.ndarray, rpm: float, fs: int = FS_HZ) -> dict[str, float]:
    """Extract stable scalar features from one vibration window."""
    values = np.asarray(signal, dtype=np.float64)
    centered = values - values.mean()
    rms = float(np.sqrt(np.mean(centered**2)))
    absolute_peak = float(np.max(np.abs(centered)))
    time_features = {
        "rms": rms,
        "kurtosis": float(kurtosis(centered, fisher=True, bias=False)),
        "skewness": float(skew(centered, bias=False)),
        "crest_factor": absolute_peak / (rms + 1e-12),
        "peak_to_peak": float(np.ptp(values)),
        "mean_absolute": float(np.mean(np.abs(centered))),
    }

    spectrum = np.abs(np.fft.rfft(centered))
    frequencies = np.fft.rfftfreq(len(centered), 1.0 / fs)
    power = spectrum**2
    total_power = float(power.sum()) + 1e-12
    spectral_centroid = float(np.sum(frequencies * spectrum) / (spectrum.sum() + 1e-12))
    normalized_power = power / total_power
    spectral_entropy = float(-np.sum(normalized_power * np.log(normalized_power + 1e-12)))
    frequency_features: dict[str, float] = {
        "spectral_centroid": spectral_centroid,
        "spectral_entropy": spectral_entropy,
        "dominant_frequency": float(frequencies[np.argmax(spectrum)]),
    }
    for lower, upper in ((0, 500), (500, 1500), (1500, 2500), (2500, 4000), (4000, 6000)):
        band = (frequencies >= lower) & (frequencies < upper)
        frequency_features[f"band_energy_{lower}_{upper}"] = float(power[band].sum() / total_power)

    resonance = sosfilt(butter(4, [2000, 4000], btype="bandpass", fs=fs, output="sos"), centered)
    envelope = np.abs(hilbert(resonance))
    envelope = envelope - envelope.mean()
    envelope_spectrum = np.abs(np.fft.rfft(envelope))
    envelope_frequencies = np.fft.rfftfreq(len(envelope), 1.0 / fs)
    envelope_power = envelope_spectrum**2
    envelope_total = float(envelope_power.sum()) + 1e-12
    frequencies_for_rpm = fault_frequencies(rpm)
    envelope_features: dict[str, float] = {
        "envelope_rms": float(np.sqrt(np.mean(envelope**2))),
        "envelope_spectral_centroid": float(
            np.sum(envelope_frequencies * envelope_spectrum) / (envelope_spectrum.sum() + 1e-12)
        ),
    }
    for name in ("bpfo", "bpfi", "bsf", "ftf"):
        target = getattr(frequencies_for_rpm, name)
        width = max(fs / len(values) * 1.5, target * 0.035)
        mask = np.abs(envelope_frequencies - target) <= width
        envelope_features[f"envelope_{name}_energy"] = float(envelope_power[mask].sum() / envelope_total)
        harmonics = np.abs(envelope_frequencies - 2 * target) <= max(width, target * 0.07)
        envelope_features[f"envelope_{name}_harmonic_energy"] = float(
            envelope_power[harmonics].sum() / envelope_total
        )
    return {**time_features, **frequency_features, **envelope_features}


def build_feature_table(
    signals: np.ndarray, metadata: pd.DataFrame, fs: int = FS_HZ
) -> pd.DataFrame:
    """Extract a feature row per signal and retain source metadata."""
    rows = [extract_features(signal, float(row.rpm), fs) for signal, row in zip(signals, metadata.itertuples())]
    return pd.concat([metadata.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def extract_classification_features(data_dir: Path = ROOT / "data") -> pd.DataFrame:
    with np.load(data_dir / "classification_windows.npz") as archive:
        signals = archive["signals"]
    metadata = pd.read_csv(data_dir / "classification_metadata.csv")
    table = build_feature_table(signals, metadata)
    table.to_csv(data_dir / "features.csv", index=False)
    print(f"Saved {len(table)} feature rows to {data_dir / 'features.csv'}")
    return table


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    extract_classification_features(parser.parse_args().data_dir)