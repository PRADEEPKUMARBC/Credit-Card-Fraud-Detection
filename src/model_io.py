"""
model_io.py
-----------
Centralized load/save helpers for the trained model, scaler, metadata,
and metrics. Used by train.py, evaluate.py, predict.py, and the
FastAPI backend.

Artifacts on disk (inside models/):
    fraud_detection_model.pkl   : trained RandomForestClassifier
    scaler.pkl                  : fitted StandardScaler
    training_metadata.json      : feature names, scaled columns, model info
    metrics.json                : last computed evaluation metrics
    model_info.txt              : human-readable summary
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from preprocessing import MODELS_DIR


# ---------------------------------------------------------------------------
# Canonical file paths
# ---------------------------------------------------------------------------
MODEL_PATH = MODELS_DIR / "fraud_detection_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
METADATA_PATH = MODELS_DIR / "training_metadata.json"
METRICS_PATH = MODELS_DIR / "metrics.json"
INFO_PATH = MODELS_DIR / "model_info.txt"


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
def save_model(model: Any, path: Path = MODEL_PATH) -> Path:
    """Persist a fitted model with joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    print(f"[model_io] Model saved  -> {path}")
    return path


def save_scaler(scaler: Any, path: Path = SCALER_PATH) -> Path:
    """Persist a fitted scaler with joblib."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, path)
    print(f"[model_io] Scaler saved -> {path}")
    return path


def save_metadata(metadata: dict, path: Path = METADATA_PATH) -> Path:
    """Persist metadata (feature names, scaled columns, model type, etc.)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[model_io] Metadata saved -> {path}")
    return path


def save_metrics(metrics: dict, path: Path = METRICS_PATH) -> Path:
    """Persist the latest evaluation metrics."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[model_io] Metrics saved -> {path}")
    return path


def save_model_info(
    model: Any,
    metadata: dict,
    metrics: dict | None = None,
    path: Path = INFO_PATH,
) -> Path:
    """
    Write a human-readable summary of the trained model to a text file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("=" * 65)
    lines.append("CREDIT CARD FRAUD DETECTION - MODEL SUMMARY")
    lines.append("=" * 65)
    lines.append(f"Generated at      : {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Model type        : {type(model).__name__}")

    if hasattr(model, "n_estimators"):
        lines.append(f"Number of trees   : {model.n_estimators}")
    if hasattr(model, "max_depth"):
        lines.append(f"Max depth         : {model.max_depth}")
    if hasattr(model, "n_features_in_"):
        lines.append(f"Features in       : {model.n_features_in_}")

    lines.append("")
    lines.append("Preprocessing")
    lines.append("-" * 65)
    lines.append(f"Scaled columns    : {metadata.get('scaled_columns', [])}")
    lines.append(f"Target column     : {metadata.get('target_column', 'Class')}")
    lines.append(f"Random state      : {metadata.get('random_state', 'n/a')}")
    feature_names = metadata.get("feature_names", [])
    lines.append(f"Feature count     : {len(feature_names)}")
    lines.append(f"Feature names     : {feature_names}")

    if metrics:
        lines.append("")
        lines.append("Evaluation Metrics (test set)")
        lines.append("-" * 65)
        for key in [
            "accuracy", "precision", "recall", "f1_score", "roc_auc",
            "true_positives", "true_negatives",
            "false_positives", "false_negatives",
            "test_set_size", "actual_frauds", "predicted_frauds",
        ]:
            if key in metrics:
                value = metrics[key]
                if isinstance(value, float):
                    lines.append(f"{key:<20}: {value:.4f}")
                else:
                    lines.append(f"{key:<20}: {value}")

    lines.append("")
    lines.append("=" * 65)

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[model_io] Model info saved -> {path}")
    return path


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
def _require(path: Path, friendly_name: str, hint: str) -> None:
    """Raise a helpful error if an expected artifact is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"{friendly_name} not found at:\n  {path}\n"
            f"Hint: {hint}"
        )


def load_model(path: Path = MODEL_PATH):
    """Load the trained model with joblib."""
    _require(path, "Trained model", "Run 'python src/train.py' first.")
    model = joblib.load(path)
    return model


def load_scaler(path: Path = SCALER_PATH):
    """Load the fitted scaler with joblib."""
    _require(path, "Scaler", "Run 'python src/train.py' first.")
    scaler = joblib.load(path)
    return scaler


def load_metadata(path: Path = METADATA_PATH) -> dict:
    """Load the training metadata JSON file."""
    _require(path, "Metadata", "Run 'python src/train.py' first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_metrics(path: Path = METRICS_PATH) -> dict:
    """Load the latest evaluation metrics JSON file."""
    _require(path, "Metrics", "Run 'python src/evaluate.py' first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def artifacts_exist() -> bool:
    """Return True if all essential artifacts exist on disk."""
    return all(p.exists() for p in (MODEL_PATH, SCALER_PATH, METADATA_PATH))