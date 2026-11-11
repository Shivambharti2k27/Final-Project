"""Train grouped classical and 1-D CNN fault classifiers."""

from __future__ import annotations

import json
import random
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.result_store import ROOT, update_metrics
from src.simulator import FAULT_TYPES

SEED = 2026
CLASS_NAMES = list(FAULT_TYPES)
EXCLUDED = {"window_id", "run_id", "fault_type", "label", "domain", "severity", "snr_db"}


class SignalCNN(nn.Module):
    """Compact raw-waveform classifier for CPU training."""

    def __init__(self, number_of_classes: int = 4) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=17, stride=4, padding=8), nn.BatchNorm1d(16), nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=9, stride=2, padding=4), nn.BatchNorm1d(32), nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=7, stride=2, padding=3), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1), nn.Flatten(),
            nn.Linear(64, 48), nn.ReLU(), nn.Dropout(0.15), nn.Linear(48, number_of_classes),
        )

    def forward(self, signals: torch.Tensor) -> torch.Tensor:
        return self.encoder(signals)


def grouped_indices(metadata: pd.DataFrame, seed: int = SEED) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Stratify run IDs, then map them back to window indices."""
    runs = metadata[["run_id", "label"]].drop_duplicates()
    train_runs, remainder = train_test_split(
        runs.run_id.to_numpy(), test_size=0.30, random_state=seed,
        stratify=runs.label.to_numpy(),
    )
    remainder_rows = runs.set_index("run_id").loc[remainder]
    validation_runs, test_runs = train_test_split(
        remainder, test_size=0.50, random_state=seed + 1,
        stratify=remainder_rows.label.to_numpy(),
    )
    groups = metadata.run_id.to_numpy()
    return tuple(np.flatnonzero(np.isin(groups, split)) for split in (train_runs, validation_runs, test_runs))


def _scores(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(truth, prediction)),
        "precision_weighted": float(precision_score(truth, prediction, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(truth, prediction, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(truth, prediction, average="weighted", zero_division=0)),
    }


def _plot_confusion(truth: np.ndarray, prediction: np.ndarray, path: Path, title: str) -> None:
    matrix = confusion_matrix(truth, prediction, labels=np.arange(len(CLASS_NAMES)))
    fig, axis = plt.subplots(figsize=(6.4, 5.2))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="crest", xticklabels=CLASS_NAMES,
                yticklabels=CLASS_NAMES, ax=axis)
    axis.set(xlabel="Predicted", ylabel="Actual", title=title)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _fit_cnn(
    signals: np.ndarray, labels: np.ndarray, train_idx: np.ndarray, validation_idx: np.ndarray,
    test_idx: np.ndarray, output_dir: Path, epochs: int = 3,
) -> tuple[dict[str, float], np.ndarray]:
    torch.manual_seed(SEED)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    model = SignalCNN()
    train_signals = torch.from_numpy(signals[train_idx, None, :].astype(np.float32))
    train_labels = torch.from_numpy(labels[train_idx].astype(np.int64))
    validation_signals = torch.from_numpy(signals[validation_idx, None, :].astype(np.float32))
    validation_labels = torch.from_numpy(labels[validation_idx].astype(np.int64))
    train_loader = DataLoader(TensorDataset(train_signals, train_labels), batch_size=64, shuffle=True,
                              generator=torch.Generator().manual_seed(SEED))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_function = nn.CrossEntropyLoss()
    best_loss = float("inf")
    best_state = None
    for _ in range(epochs):
        model.train()
        for batch, target in train_loader:
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(batch), target)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            validation_loss = loss_function(model(validation_signals), validation_labels).item()
        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    test_tensor = torch.from_numpy(signals[test_idx, None, :].astype(np.float32))
    with torch.no_grad():
        prediction = model(test_tensor).argmax(dim=1).numpy()
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_dir / "classification_cnn.pt")
    return _scores(labels[test_idx], prediction), prediction


def train_classifiers(root: Path = ROOT, cnn_epochs: int = 3) -> dict[str, object]:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    data_dir = root / "data"
    results_dir = root / "results"
    figure_dir = results_dir / "figures"
    model_dir = root / "models"
    figure_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    features = pd.read_csv(data_dir / "features.csv")
    metadata = pd.read_csv(data_dir / "classification_metadata.csv")
    with np.load(data_dir / "classification_windows.npz") as archive:
        signals = archive["signals"]
    feature_columns = [column for column in features.select_dtypes(include=[np.number]) if column not in EXCLUDED]
    x = features[feature_columns].replace([np.inf, -np.inf], np.nan)
    x = x.fillna(x.median()).to_numpy(dtype=np.float32)
    y = metadata.label.to_numpy(dtype=np.int64)
    train_idx, validation_idx, test_idx = grouped_indices(metadata)

    estimators = {
        "SVM": make_pipeline(StandardScaler(), SVC(C=3, kernel="rbf", class_weight="balanced")),
        "Random Forest": RandomForestClassifier(n_estimators=240, min_samples_leaf=2,
                                                  class_weight="balanced", n_jobs=-1, random_state=SEED),
        "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=7, weights="distance")),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=120, learning_rate=0.06,
                                                          max_depth=2, random_state=SEED),
    }
    classical: dict[str, dict[str, float]] = {}
    fitted: dict[str, object] = {}
    for name, estimator in estimators.items():
        estimator.fit(x[train_idx], y[train_idx])
        validation_prediction = estimator.predict(x[validation_idx])
        test_prediction = estimator.predict(x[test_idx])
        classical[name] = {**_scores(y[test_idx], test_prediction),
                           "validation_f1_weighted": _scores(y[validation_idx], validation_prediction)["f1_weighted"]}
        fitted[name] = estimator
        safe_name = name.lower().replace(" ", "_")
        _plot_confusion(y[test_idx], test_prediction, figure_dir / f"{safe_name}_confusion.png",
                        f"{name}, held-out bearing runs")

    best_name = max(classical, key=lambda model_name: classical[model_name]["validation_f1_weighted"])
    best_model = fitted[best_name]
    joblib.dump(best_model, model_dir / "fault_classifier.joblib")
    (model_dir / "fault_feature_columns.json").write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")
    selected_prediction = best_model.predict(x[test_idx])
    _plot_confusion(y[test_idx], selected_prediction, figure_dir / "best_classifier_confusion.png",
                    f"{best_name}, held-out bearing runs")

    noise_robustness: dict[str, float] = {}
    noise_values = metadata.snr_db.to_numpy()
    for snr in (0, 5, 10, 15, 20):
        subset = test_idx[noise_values[test_idx] == snr]
        if len(subset):
            noise_robustness[str(snr)] = float(f1_score(y[subset], best_model.predict(x[subset]),
                                                         average="weighted", zero_division=0))
    fig, axis = plt.subplots(figsize=(6.4, 4.2))
    axis.plot([int(value) for value in noise_robustness], list(noise_robustness.values()), marker="o")
    axis.set(xlabel="Signal-to-noise ratio (dB)", ylabel="Weighted F1", ylim=(0, 1.02),
             title="Held-out run performance by noise level")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_dir / "noise_robustness.png", dpi=160)
    plt.close(fig)

    low_idx = np.flatnonzero((metadata.domain.to_numpy() == "low") & np.isin(np.arange(len(metadata)), train_idx))
    high_idx = np.flatnonzero(metadata.domain.to_numpy() == "high")
    domain_model = fitted[best_name]
    domain_model.fit(x[low_idx], y[low_idx])
    high_prediction = domain_model.predict(x[high_idx])
    domain_scores = _scores(y[high_idx], high_prediction)
    cnn_scores, cnn_prediction = _fit_cnn(signals, y, train_idx, validation_idx, test_idx,
                                          model_dir, epochs=cnn_epochs)
    _plot_confusion(y[test_idx], cnn_prediction, figure_dir / "cnn_confusion.png",
                    "1-D CNN, held-out bearing runs")
    report: dict[str, object] = {
        "dataset_windows": int(len(metadata)),
        "independent_runs": int(metadata.run_id.nunique()),
        "split_run_counts": {
            "train": int(metadata.iloc[train_idx].run_id.nunique()),
            "validation": int(metadata.iloc[validation_idx].run_id.nunique()),
            "test": int(metadata.iloc[test_idx].run_id.nunique()),
        },
        "classical_models": classical,
        "best_classical_model": best_name,
        "best_classical_test": classical[best_name],
        "cnn_test": cnn_scores,
        "noise_robustness_weighted_f1": noise_robustness,
        "low_to_high_speed_load_test": domain_scores,
        "low_domain_train_windows": int(len(low_idx)),
        "high_domain_test_windows": int(len(high_idx)),
        "confusion_matrices": [
            "svm_confusion.png", "random_forest_confusion.png", "knn_confusion.png",
            "gradient_boosting_confusion.png", "best_classifier_confusion.png", "cnn_confusion.png",
        ],
    }
    update_metrics("classification", report)
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    train_classifiers()