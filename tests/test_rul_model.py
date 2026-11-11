"""Regression checks for the temporal RUL CNN input and output shapes."""

import torch

from src.train_rul import TemporalCNN


def test_temporal_cnn_accepts_feature_channel_first_sequences() -> None:
    model = TemporalCNN(feature_count=23)
    predictions = model(torch.zeros((5, 23, 8), dtype=torch.float32))
    assert predictions.shape == (5,)