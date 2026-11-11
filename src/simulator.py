"""Physics-based vibration synthesis for a 6205 deep-groove ball bearing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import NDArray
from scipy.signal import butter, sosfilt

FS_HZ = 12_000
BEARING_GEOMETRY = {
    "rolling_elements": 9,
    "ball_diameter_mm": 7.938,
    "pitch_diameter_mm": 39.04,
    "contact_angle_deg": 0.0,
}
FAULT_TYPES = ("Healthy", "Inner Race", "Outer Race", "Ball")


@dataclass(frozen=True)
class FaultFrequencies:
    """Characteristic frequencies in hertz for one shaft speed."""

    bpfo: float
    bpfi: float
    bsf: float
    ftf: float


def fault_frequencies(rpm: float, geometry: dict[str, float] | None = None) -> FaultFrequencies:
    """Calculate bearing frequencies using standard rolling-element kinematics."""
    dimensions = geometry or BEARING_GEOMETRY
    count = dimensions["rolling_elements"]
    ratio = dimensions["ball_diameter_mm"] / dimensions["pitch_diameter_mm"]
    angle = np.deg2rad(dimensions["contact_angle_deg"])
    shaft_hz = rpm / 60.0
    cosine = np.cos(angle)
    return FaultFrequencies(
        bpfo=count / 2.0 * shaft_hz * (1.0 - ratio * cosine),
        bpfi=count / 2.0 * shaft_hz * (1.0 + ratio * cosine),
        bsf=dimensions["pitch_diameter_mm"] / (2.0 * dimensions["ball_diameter_mm"])
        * shaft_hz * (1.0 - (ratio * cosine) ** 2),
        ftf=0.5 * shaft_hz * (1.0 - ratio * cosine),
    )


def _colored_noise(rng: np.random.Generator, size: int) -> NDArray[np.float64]:
    white = rng.standard_normal(size)
    sos = butter(2, 0.18, btype="lowpass", output="sos")
    return sosfilt(sos, white)


def simulate_signal(
    fault_type: str,
    rpm: float = 1800.0,
    load: float = 1.0,
    severity: float = 0.6,
    snr_db: float = 10.0,
    n_samples: int = 4096,
    fs: int = FS_HZ,
    rng: np.random.Generator | None = None,
) -> NDArray[np.float32]:
    """Create a noisy vibration window with fault impacts and resonant ringing.

    Fault impacts follow the appropriate kinematic frequency. Inter-impact timing
    receives 1.5% Gaussian jitter, while the impact envelope varies at shaft speed
    (or cage frequency for rolling-element faults).
    """
    if fault_type not in (*FAULT_TYPES, "Combined"):
        raise ValueError(f"Unsupported fault type: {fault_type}")
    if not 1500 <= rpm <= 3000:
        raise ValueError("rpm must be between 1500 and 3000")
    if n_samples <= 0 or fs <= 0:
        raise ValueError("n_samples and fs must be positive")
    generator = rng or np.random.default_rng()
    severity = float(np.clip(severity, 0.0, 1.0))
    load = float(np.clip(load, 0.2, 2.0))
    duration = n_samples / fs
    time = np.arange(n_samples, dtype=np.float64) / fs
    shaft_hz = rpm / 60.0
    signal = 0.018 * np.sin(2 * np.pi * shaft_hz * time)
    signal += 0.008 * np.sin(2 * np.pi * 2 * shaft_hz * time + 0.4)

    if fault_type != "Healthy" and severity > 0:
        frequencies = fault_frequencies(rpm)
        selected: Iterable[tuple[str, float]]
        if fault_type == "Combined":
            selected = (("Inner Race", frequencies.bpfi), ("Outer Race", frequencies.bpfo))
        else:
            selected = ((fault_type, {
                "Inner Race": frequencies.bpfi,
                "Outer Race": frequencies.bpfo,
                "Ball": frequencies.bsf,
            }[fault_type]),)
        decay_samples = min(int(0.012 * fs), n_samples)
        ring_time = np.arange(decay_samples) / fs
        resonance = 3000.0 + generator.uniform(-350.0, 350.0)
        decay = np.exp(-ring_time / 0.0015) * np.sin(2 * np.pi * resonance * ring_time)
        for selected_type, impact_hz in selected:
            interval = 1.0 / impact_hz
            event_time = generator.uniform(0.0, interval)
            while event_time < duration:
                phase = 2 * np.pi * shaft_hz * event_time
                if selected_type == "Inner Race":
                    modulation = 0.65 + 0.35 * np.cos(phase)
                elif selected_type == "Ball":
                    modulation = 0.60 + 0.40 * np.cos(2 * np.pi * frequencies.ftf * event_time)
                else:
                    modulation = 0.75 + 0.25 * np.cos(phase)
                amplitude = severity * np.sqrt(load) * modulation
                start = int(round(event_time * fs))
                stop = min(start + decay_samples, n_samples)
                if start < n_samples:
                    signal[start:stop] += amplitude * decay[: stop - start]
                event_time += interval * (1.0 + generator.normal(0.0, 0.015))

    clean_rms = float(np.sqrt(np.mean(signal**2)))
    gaussian = generator.standard_normal(n_samples)
    colored = _colored_noise(generator, n_samples)
    noise = 0.72 * gaussian + 0.28 * colored / (np.std(colored) + 1e-12)
    noise_rms = clean_rms / (10 ** (snr_db / 20.0))
    noise *= noise_rms / (np.std(noise) + 1e-12)
    return (signal + noise).astype(np.float32)


def expected_fault_frequency(fault_type: str, rpm: float) -> float | None:
    """Return the fundamental defect frequency used for spectrum markers."""
    frequencies = fault_frequencies(rpm)
    return {
        "Inner Race": frequencies.bpfi,
        "Outer Race": frequencies.bpfo,
        "Ball": frequencies.bsf,
    }.get(fault_type)