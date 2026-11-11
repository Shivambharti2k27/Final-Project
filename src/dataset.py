"""Create a deterministic, run-grouped synthetic classification dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.simulator import FAULT_TYPES, FS_HZ, simulate_signal

ROOT = Path(__file__).resolve().parents[1]


def generate_dataset(windows_per_fault: int = 1000, seed: int = 2026) -> tuple[np.ndarray, pd.DataFrame]:
    """Generate labeled windows from distinct simulated bearing runs.

    Each fault class has 20 independent run IDs. Half operate in a lower
    speed/load band and half in a higher band, enabling group and domain tests.
    """
    if windows_per_fault < 20 or windows_per_fault % 20:
        raise ValueError("windows_per_fault must be at least 20 and divisible by 20")
    rng = np.random.default_rng(seed)
    per_run = windows_per_fault // 20
    signals = np.empty((len(FAULT_TYPES) * windows_per_fault, 4096), dtype=np.float32)
    records: list[dict[str, object]] = []
    cursor = 0
    for label, fault_type in enumerate(FAULT_TYPES):
        for run_number in range(20):
            domain = "low" if run_number < 10 else "high"
            if domain == "low":
                base_rpm = rng.uniform(1500, 2150)
                base_load = rng.uniform(0.35, 1.15)
            else:
                base_rpm = rng.uniform(2350, 3000)
                base_load = rng.uniform(1.05, 2.0)
            run_id = f"{label}-{run_number:02d}"
            for _ in range(per_run):
                rpm = float(np.clip(base_rpm + rng.normal(0, 18), 1500, 3000))
                load = float(np.clip(base_load + rng.normal(0, 0.06), 0.2, 2.0))
                severity = 0.0 if fault_type == "Healthy" else float(rng.uniform(0.25, 0.95))
                snr_db = float(rng.choice([0, 5, 10, 15, 20]))
                signals[cursor] = simulate_signal(
                    fault_type, rpm, load, severity, snr_db, 4096, FS_HZ, rng
                )
                records.append({
                    "window_id": cursor,
                    "run_id": run_id,
                    "fault_type": fault_type,
                    "label": label,
                    "rpm": rpm,
                    "load": load,
                    "severity": severity,
                    "snr_db": snr_db,
                    "domain": domain,
                })
                cursor += 1
    return signals, pd.DataFrame.from_records(records)


def save_dataset(windows_per_fault: int = 1000, seed: int = 2026, output_dir: Path = ROOT / "data") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    signals, metadata = generate_dataset(windows_per_fault, seed)
    np.savez_compressed(output_dir / "classification_windows.npz", signals=signals)
    metadata.to_csv(output_dir / "classification_metadata.csv", index=False)
    print(f"Saved {len(metadata)} windows across {metadata.run_id.nunique()} runs to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows-per-fault", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    save_dataset(args.windows_per_fault, args.seed)