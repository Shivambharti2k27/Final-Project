"""Generate seeded run-to-failure bearing histories with true RUL labels."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.simulator import FAULT_TYPES, FS_HZ, simulate_signal

ROOT = Path(__file__).resolve().parents[1]
FAILURE_THRESHOLD = 0.90


def simulate_life_histories(
    bearing_count: int = 30, steps_per_life: int = 40, seed: int = 2027
) -> tuple[np.ndarray, pd.DataFrame]:
    """Synthesize progressive fault histories; labels are hours to threshold."""
    if bearing_count < 3 or steps_per_life < 10:
        raise ValueError("Use at least three lives and ten observations per life")
    rng = np.random.default_rng(seed)
    signals = np.empty((bearing_count * steps_per_life, 4096), dtype=np.float32)
    rows: list[dict[str, object]] = []
    cursor = 0
    fault_choices = FAULT_TYPES[1:]
    for bearing_index in range(bearing_count):
        life_id = f"L{bearing_index:03d}"
        fault_type = str(rng.choice(fault_choices))
        rpm = float(rng.uniform(1500, 3000))
        load = float(rng.uniform(0.5, 1.8))
        failure_hours = float(rng.uniform(40, 100))
        times = np.linspace(0.0, failure_hours, steps_per_life)
        growth_rate = np.log(FAILURE_THRESHOLD / 0.025) / failure_hours
        for time_hours in times:
            nominal_severity = 0.025 * np.exp(growth_rate * time_hours)
            severity = float(np.clip(nominal_severity * rng.lognormal(0, 0.055), 0.01, 0.98))
            snr_db = float(rng.uniform(5, 20))
            signals[cursor] = simulate_signal(
                fault_type, rpm, load, severity, snr_db, 4096, FS_HZ, rng
            )
            health_indicator = float(np.clip(severity + rng.normal(0, 0.025), 0, 1))
            rows.append({
                "window_id": cursor,
                "life_id": life_id,
                "fault_type": fault_type,
                "rpm": rpm,
                "load": load,
                "age_hours": float(time_hours),
                "failure_hours": failure_hours,
                "severity": severity,
                "health_indicator": health_indicator,
                "rul_hours": float(max(failure_hours - time_hours, 0.0)),
                "failure_threshold": FAILURE_THRESHOLD,
                "snr_db": snr_db,
            })
            cursor += 1
    return signals, pd.DataFrame.from_records(rows)


def save_life_histories(
    bearing_count: int = 30, steps_per_life: int = 40, seed: int = 2027,
    output_dir: Path = ROOT / "data",
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    signals, metadata = simulate_life_histories(bearing_count, steps_per_life, seed)
    np.savez_compressed(output_dir / "degradation_windows.npz", signals=signals)
    metadata.to_csv(output_dir / "degradation_metadata.csv", index=False)
    print(f"Saved {len(metadata)} degradation observations across {bearing_count} lives")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bearing-count", type=int, default=30)
    parser.add_argument("--steps-per-life", type=int, default=40)
    parser.add_argument("--seed", type=int, default=2027)
    args = parser.parse_args()
    save_life_histories(args.bearing_count, args.steps_per_life, args.seed)