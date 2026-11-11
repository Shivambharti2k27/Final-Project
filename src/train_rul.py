"""Train grouped-life classical and temporal CNN RUL predictors."""

from __future__ import annotations

import json
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.features import build_feature_table
from src.result_store import ROOT, update_metrics

SEED = 2027
RUL_EXCLUDED = {
    "window_id", "life_id", "fault_type", "age_hours", "failure_hours", "severity",
    "rul_hours", "failure_threshold", "snr_db",
}
SEQUENCE_LENGTH = 8


class TemporalCNN(nn.Module):
    """Regress RUL from recent feature history using a compact 1-D CNN."""

    def __init__(self, feature_count: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv1d(feature_count, 24, kernel_size=3, padding=1), nn.ReLU(),
            nn.Conv1d(24, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(32, 24), nn.ReLU(), nn.Linear(24, 1),
        )

    def forward(self, sequence: torch.Tensor) -> torch.Tensor:
        return self.network(sequence).squeeze(1)


def asymmetric_rul_score(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean NASA-style asymmetric penalty; late predictions are penalized more."""
    error = np.asarray(predicted) - np.asarray(actual)
    penalties = np.where(error < 0, np.exp(-error / 10.0) - 1.0, np.exp(error / 13.0) - 1.0)
    return float(np.mean(penalties))


def _make_sequences(
    scaled_features: np.ndarray, labels: np.ndarray, metadata: pd.DataFrame, allowed_lives: set[str]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sequences: list[np.ndarray] = []
    targets: list[float] = []
    life_ids: list[str] = []
    for life_id, indices in metadata.groupby("life_id", sort=False).indices.items():
        if life_id not in allowed_lives:
            continue
        ordered = np.asarray(indices)
        for position, row_index in enumerate(ordered):
            start = max(0, position - SEQUENCE_LENGTH + 1)
            context = scaled_features[ordered[start: position + 1]]
            if len(context) < SEQUENCE_LENGTH:
                padding = np.repeat(context[:1], SEQUENCE_LENGTH - len(context), axis=0)
                context = np.concatenate((padding, context), axis=0)
            sequences.append(context)
            targets.append(float(labels[row_index]))
            life_ids.append(str(life_id))
    return np.asarray(sequences, dtype=np.float32), np.asarray(targets, dtype=np.float32), np.asarray(life_ids)


def train_rul_models(root: Path = ROOT, cnn_epochs: int = 18) -> dict[str, object]:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    data_dir = root / "data"
    results_dir = root / "results"
    figure_dir = results_dir / "figures"
    model_dir = root / "models"
    figure_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    with np.load(data_dir / "degradation_windows.npz") as archive:
        signals = archive["signals"]
    metadata = pd.read_csv(data_dir / "degradation_metadata.csv")
    if len(metadata) != len(signals):
        raise ValueError("Degradation signals and metadata do not align")
    feature_table = build_feature_table(signals, metadata)
    feature_table.to_csv(data_dir / "rul_features.csv", index=False)
    columns = [name for name in feature_table.select_dtypes(include=[np.number]) if name not in RUL_EXCLUDED]
    x = feature_table[columns].replace([np.inf, -np.inf], np.nan)
    x = x.fillna(x.median()).to_numpy(dtype=np.float32)
    y = metadata.rul_hours.to_numpy(dtype=np.float32)
    life_rows = metadata[["life_id", "fault_type"]].drop_duplicates()
    train_lives, remainder = train_test_split(life_rows.life_id.to_numpy(), test_size=0.30,
                                              random_state=SEED, stratify=life_rows.fault_type)
    remainder_table = life_rows.set_index("life_id").loc[remainder]
    validation_lives, test_lives = train_test_split(remainder, test_size=0.50, random_state=SEED + 1,
                                                    stratify=remainder_table.fault_type)
    train_idx = np.flatnonzero(metadata.life_id.isin(train_lives))
    validation_idx = np.flatnonzero(metadata.life_id.isin(validation_lives))
    test_idx = np.flatnonzero(metadata.life_id.isin(test_lives))
    estimators = {
        "Random Forest": RandomForestRegressor(n_estimators=240, min_samples_leaf=2,
                                                n_jobs=-1, random_state=SEED),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=140, learning_rate=0.04,
                                                        max_depth=2, loss="huber", random_state=SEED),
    }
    classical: dict[str, dict[str, float]] = {}
    fitted: dict[str, object] = {}
    validation_rmse: dict[str, float] = {}
    for name, estimator in estimators.items():
        estimator.fit(x[train_idx], y[train_idx])
        validation_prediction = estimator.predict(x[validation_idx])
        prediction = estimator.predict(x[test_idx])
        classical[name] = {
            "rmse_hours": float(np.sqrt(mean_squared_error(y[test_idx], prediction))),
            "mae_hours": float(mean_absolute_error(y[test_idx], prediction)),
            "asymmetric_score": asymmetric_rul_score(y[test_idx], prediction),
        }
        validation_rmse[name] = float(np.sqrt(mean_squared_error(y[validation_idx], validation_prediction)))
        fitted[name] = estimator
    best_name = min(validation_rmse, key=validation_rmse.get)
    import joblib
    joblib.dump(fitted[best_name], model_dir / "rul_regressor.joblib")
    joblib.dump({"columns": columns, "median": feature_table[columns].median().to_dict()},
                model_dir / "rul_preprocessing.joblib")

    scaler = StandardScaler().fit(x[train_idx])
    scaled = scaler.transform(x).astype(np.float32)
    train_sequences, train_targets, _ = _make_sequences(scaled, y, metadata, set(train_lives))
    validation_sequences, validation_targets, _ = _make_sequences(scaled, y, metadata, set(validation_lives))
    test_sequences, test_targets, test_sequence_lives = _make_sequences(scaled, y, metadata, set(test_lives))
    target_scale = float(np.max(train_targets))
    train_tensor = torch.from_numpy(np.transpose(train_sequences, (0, 2, 1)))
    train_target_tensor = torch.from_numpy(train_targets / target_scale)
    loader = DataLoader(TensorDataset(train_tensor, train_target_tensor), batch_size=64, shuffle=True,
                        generator=torch.Generator().manual_seed(SEED))
    model = TemporalCNN(len(columns))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    loss_function = nn.SmoothL1Loss()
    validation_tensor = torch.from_numpy(np.transpose(validation_sequences, (0, 2, 1)))
    validation_target_tensor = torch.from_numpy(validation_targets / target_scale)
    best_loss = float("inf")
    best_state = None
    for _ in range(cnn_epochs):
        model.train()
        for batch, target in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(batch), target)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            current_loss = loss_function(model(validation_tensor), validation_target_tensor).item()
        if current_loss < best_loss:
            best_loss = current_loss
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        test_tensor = torch.from_numpy(np.transpose(test_sequences, (0, 2, 1)))
        cnn_prediction = model(test_tensor).numpy() * target_scale
    cnn_metrics = {
        "rmse_hours": float(np.sqrt(mean_squared_error(test_targets, cnn_prediction))),
        "mae_hours": float(mean_absolute_error(test_targets, cnn_prediction)),
        "asymmetric_score": asymmetric_rul_score(test_targets, cnn_prediction),
    }
    torch.save({"state_dict": model.state_dict(), "feature_count": len(columns),
                "target_scale": target_scale, "sequence_length": SEQUENCE_LENGTH,
                "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist()},
               model_dir / "rul_temporal_cnn.pt")

    # Plot one held-out life, preserving chronological order.
    selected_life = str(test_lives[0])
    life_positions = np.flatnonzero(test_sequence_lives == selected_life)
    fig, axis = plt.subplots(figsize=(7, 4.2))
    axis.plot(test_targets[life_positions], label="True RUL", linewidth=2)
    axis.plot(cnn_prediction[life_positions], label="Temporal CNN prediction", linewidth=1.8)
    axis.set(xlabel="Observation along held-out life", ylabel="RUL (hours)",
             title=f"Run-to-failure RUL, held-out life {selected_life}")
    axis.legend()
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_dir / "rul_prediction.png", dpi=160)
    plt.close(fig)

    report: dict[str, object] = {
        "life_histories": int(metadata.life_id.nunique()),
        "observations": int(len(metadata)),
        "split_life_counts": {"train": len(train_lives), "validation": len(validation_lives), "test": len(test_lives)},
        "classical_models": classical,
        "classical_validation_rmse_hours": validation_rmse,
        "best_classical_model": best_name,
        "temporal_cnn_test": cnn_metrics,
        "score_definition": "Mean exp(-error/10)-1 for early predictions; exp(error/13)-1 for late predictions, error=predicted-true RUL.",
        "held_out_life_example": selected_life,
        "input_health_indicator": "Noisy severity-derived HI is included; direct severity and age are excluded.",
    }
    update_metrics("rul", report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    train_rul_models()