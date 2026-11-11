"""Smoke tests for deterministic data and feature generation."""

import numpy as np

from src.dataset import generate_dataset
from src.degradation import simulate_life_histories
from src.features import extract_features


def test_classification_dataset_is_reproducible_and_grouped() -> None:
    first_signals, first_metadata = generate_dataset(windows_per_fault=20, seed=13)
    second_signals, second_metadata = generate_dataset(windows_per_fault=20, seed=13)
    assert first_signals.shape == (80, 4096)
    assert np.array_equal(first_signals, second_signals)
    assert first_metadata.run_id.nunique() == 80
    assert first_metadata.fault_type.nunique() == 4
    assert first_metadata.equals(second_metadata)


def test_features_are_finite() -> None:
    signals, _ = generate_dataset(windows_per_fault=20, seed=8)
    features = extract_features(signals[0], rpm=1800)
    assert len(features) >= 20
    assert all(np.isfinite(value) for value in features.values())


def test_degradation_rul_decreases_to_threshold() -> None:
    signals, metadata = simulate_life_histories(bearing_count=3, steps_per_life=10, seed=21)
    assert signals.shape == (30, 4096)
    assert metadata.life_id.nunique() == 3
    for _, history in metadata.groupby("life_id"):
        assert history.rul_hours.iloc[0] > history.rul_hours.iloc[-1]
        assert history.rul_hours.iloc[-1] == 0
        assert history.severity.max() >= history.failure_threshold.iloc[0] * 0.9