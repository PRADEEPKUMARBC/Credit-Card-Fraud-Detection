"""
predict.py
----------
Reusable prediction module for the Credit Card Fraud Detection project.

This module:
- Loads the trained model, scaler, and metadata ONCE at construction time
- Accepts a single transaction (or a batch) as a Python dict
- Applies the exact same preprocessing used during training
- Returns a clean, JSON-friendly dict with prediction and probability

The FastAPI backend in backend/main.py will import this class.

CLI usage (from project root):
    python src/predict.py
This runs two built-in demos: one on a real fraud row, one on a genuine row.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from model_io import load_model, load_scaler, load_metadata
from preprocessing import DATASET_PATH, TARGET_COLUMN


# ---------------------------------------------------------------------------
# Risk thresholds (fraud probability -> risk label)
# ---------------------------------------------------------------------------
RISK_THRESHOLDS = {
    "high":   0.75,   # >= 0.75  -> High risk
    "medium": 0.40,   # >= 0.40  -> Medium risk
    # below medium       -> Low risk
}


def _risk_level(prob: float) -> str:
    """Convert a fraud probability into a human-readable risk level."""
    if prob >= RISK_THRESHOLDS["high"]:
        return "High"
    if prob >= RISK_THRESHOLDS["medium"]:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Predictor class
# ---------------------------------------------------------------------------
class TransactionPredictor:
    """
    Wraps the trained model + scaler + metadata into a single reusable
    predictor. Load the artifacts once; call .predict() as often as needed.
    """

    def __init__(self) -> None:
        """Load model, scaler, and metadata from disk."""
        self.model = load_model()
        self.scaler = load_scaler()
        self.metadata = load_metadata()

        self.feature_names: list[str] = list(self.metadata["feature_names"])
        self.scaled_columns: list[str] = list(self.metadata["scaled_columns"])
        self.n_features: int = int(self.metadata["n_features"])

        print(f"[TransactionPredictor] Loaded {type(self.model).__name__} "
              f"with {self.n_features} features.")
        print(f"[TransactionPredictor] Scaled columns: {self.scaled_columns}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def predict(self, transaction: dict[str, Any]) -> dict[str, Any]:
        """
        Predict a single transaction.

        Parameters
        ----------
        transaction : dict
            Must contain all required feature keys (Time, V1..V28, Amount).
            The target column ('Class') is ignored if present.

        Returns
        -------
        dict with keys:
            prediction        : 'Fraudulent' or 'Genuine'
            class             : 1 or 0
            fraud_probability : float in [0, 1]
            risk_level        : 'Low' | 'Medium' | 'High'
            threshold_used    : 0.5 (default decision threshold)
        """
        # Validate and align into a single-row dataframe
        row_df = self._prepare_input(transaction)

        # Scale the designated columns
        row_df[self.scaled_columns] = self.scaler.transform(
            row_df[self.scaled_columns]
        )

        # Predict class + probability
        pred_class = int(self.model.predict(row_df)[0])
        fraud_prob = float(self.model.predict_proba(row_df)[0, 1])

        return {
            "prediction": "Fraudulent" if pred_class == 1 else "Genuine",
            "class": pred_class,
            "fraud_probability": round(fraud_prob, 4),
            "risk_level": _risk_level(fraud_prob),
            "threshold_used": 0.5,
        }

    def predict_batch(self, transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Predict a list of transactions. Returns a list of results."""
        if not transactions:
            return []

        # Build a dataframe from the list of dicts
        rows = [self._prepare_input(t, as_dict_only=True) for t in transactions]
        X = pd.DataFrame(rows, columns=self.feature_names)

        # Scale
        X[self.scaled_columns] = self.scaler.transform(X[self.scaled_columns])

        # Predict
        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)[:, 1]

        results: list[dict[str, Any]] = []
        for p_class, p_prob in zip(preds, probs):
            p_class = int(p_class)
            p_prob = float(p_prob)
            results.append({
                "prediction": "Fraudulent" if p_class == 1 else "Genuine",
                "class": p_class,
                "fraud_probability": round(p_prob, 4),
                "risk_level": _risk_level(p_prob),
                "threshold_used": 0.5,
            })
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _prepare_input(
        self,
        transaction: dict[str, Any],
        as_dict_only: bool = False,
    ) -> pd.DataFrame | dict[str, float]:
        """
        Validate the incoming transaction dictionary, ensure all required
        feature keys are present, drop any extra keys (like Class), and
        return either a single-row DataFrame or just a normalized dict.
        """
        if not isinstance(transaction, dict):
            raise TypeError(
                f"Expected a dict, got {type(transaction).__name__}."
            )

        # Drop the target column if the caller sent it by mistake
        cleaned = {k: v for k, v in transaction.items() if k != TARGET_COLUMN}

        # Check for missing features
        missing = [f for f in self.feature_names if f not in cleaned]
        if missing:
            raise ValueError(
                f"Missing required feature(s): {missing}. "
                f"Expected {self.n_features} features: {self.feature_names}."
            )

        # Extra features (not in our expected list) are dropped silently
        extras = [k for k in cleaned.keys() if k not in self.feature_names]
        if extras:
            print(f"[TransactionPredictor] Ignoring extra keys: {extras}")

        # Coerce to float and reindex to the exact training column order
        ordered = {name: float(cleaned[name]) for name in self.feature_names}

        if as_dict_only:
            return ordered

        return pd.DataFrame([ordered], columns=self.feature_names)


# ---------------------------------------------------------------------------
# Demo / CLI usage
# ---------------------------------------------------------------------------
def _load_demo_rows() -> tuple[dict, dict]:
    """
    Load one real fraud row and one real genuine row from the raw dataset
    for demonstration. This is only used in the __main__ demo, not by the
    predictor class itself.
    """
    df = pd.read_csv(DATASET_PATH)
    fraud_row = df[df["Class"] == 1].iloc[0].drop(TARGET_COLUMN).to_dict()
    genuine_row = df[df["Class"] == 0].iloc[0].drop(TARGET_COLUMN).to_dict()
    return fraud_row, genuine_row


def _demo() -> None:
    print("=" * 65)
    print("PREDICTION MODULE DEMO")
    print("=" * 65)

    predictor = TransactionPredictor()

    fraud_row, genuine_row = _load_demo_rows()

    print("\n--- Predicting a REAL FRAUD transaction from the dataset ---")
    fraud_result = predictor.predict(fraud_row)
    print(json.dumps(fraud_result, indent=2))

    print("\n--- Predicting a REAL GENUINE transaction from the dataset ---")
    genuine_result = predictor.predict(genuine_row)
    print(json.dumps(genuine_result, indent=2))

    print("\n--- Batch prediction on both rows ---")
    batch_results = predictor.predict_batch([fraud_row, genuine_row])
    print(json.dumps(batch_results, indent=2))

    print("\n" + "=" * 65)
    print("Demo complete.")
    print("=" * 65)


if __name__ == "__main__":
    _demo()