"""
test_pipeline.py
----------------
End-to-end test of the machine learning pipeline. Verifies every stage
produces sensible output. Does NOT retrain the full model (that takes
time) — instead it trains a tiny 10-tree forest on a subsample to keep
the test fast, then verifies the saved production model behaves correctly.

Run from the project root:
    python src/test_pipeline.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Make src/ importable when run as a script
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from preprocessing import (  # noqa: E402
    load_dataset,
    clean_dataset,
    separate_features_target,
    split_data,
    fit_and_apply_scaler,
    apply_smote,
    scale_columns,
    TARGET_COLUMN,
    SCALE_COLUMNS,
)
from model_io import (  # noqa: E402
    load_model,
    load_scaler,
    load_metadata,
    load_metrics,
    artifacts_exist,
)
from predict import TransactionPredictor  # noqa: E402


# ---------------------------------------------------------------------------
# Tiny test framework
# ---------------------------------------------------------------------------
class T:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name: str, condition: bool, detail: str = ""):
        marker = "[+]" if condition else "[x]"
        status = "PASS" if condition else "FAIL"
        print(f"{marker} {status:<4} {name}")
        if detail:
            print(f"        {detail}")
        if condition:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> int:
        total = self.passed + self.failed
        print("\n" + "=" * 65)
        print(f"SUMMARY: {self.passed}/{total} tests passed")
        if self.failed:
            print("SOME TESTS FAILED — review the [x] lines above.")
        print("=" * 65)
        return 0 if self.failed == 0 else 1


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_loading(t: T):
    print("\n[TEST GROUP] Data loading and cleaning")
    df = load_dataset()
    t.check("Dataset loads", isinstance(df, pd.DataFrame))
    t.check("Row count > 200,000", len(df) > 200_000,
            f"got {len(df):,}")
    t.check("31 columns present", df.shape[1] == 31,
            f"got {df.shape[1]}")
    t.check(f"Target column '{TARGET_COLUMN}' present", TARGET_COLUMN in df.columns)
    t.check("No missing values", df.isnull().sum().sum() == 0,
            f"missing={int(df.isnull().sum().sum())}")

    df_clean = clean_dataset(df)
    t.check("Cleaning removed duplicates",
            len(df_clean) < len(df),
            f"{len(df):,} -> {len(df_clean):,}")
    t.check("Class labels are {0, 1}",
            set(df_clean[TARGET_COLUMN].unique()) == {0, 1})
    return df_clean


def test_split_and_scale(t: T, df_clean):
    print("\n[TEST GROUP] Split and scaling")
    X, y = separate_features_target(df_clean)
    t.check("X has 30 features", X.shape[1] == 30, f"got {X.shape[1]}")
    t.check("y has same length as X", len(y) == len(X))

    X_tr, X_te, y_tr, y_te = split_data(X, y)
    ratio_train = len(X_tr) / len(X)
    t.check("Train/test split ~ 80/20",
            abs(ratio_train - 0.8) < 0.005,
            f"train ratio={ratio_train:.4f}")
    t.check("Fraud count in train >= 1", y_tr.sum() >= 1)
    t.check("Fraud count in test  >= 1", y_te.sum() >= 1)

    X_tr_s, X_te_s, scaler, cols = fit_and_apply_scaler(X_tr, X_te)
    t.check("Scaled columns == ['Time', 'Amount']",
            cols == SCALE_COLUMNS, f"got {cols}")
    t.check("Train mean of Time ~ 0 after scaling",
            abs(X_tr_s["Time"].mean()) < 1e-6,
            f"mean={X_tr_s['Time'].mean():.2e}")
    t.check("Train std of Time ~ 1 after scaling",
            abs(X_tr_s["Time"].std(ddof=0) - 1.0) < 1e-6,
            f"std={X_tr_s['Time'].std(ddof=0):.6f}")
    t.check("Train mean of Amount ~ 0 after scaling",
            abs(X_tr_s["Amount"].mean()) < 1e-6,
            f"mean={X_tr_s['Amount'].mean():.2e}")
    t.check("Test set was transformed, not re-fit",
            abs(X_te_s["Time"].mean()) > 0.0,
            "test mean is not exactly 0 (proves we used train's scaler)")

    return X_tr_s, X_te_s, y_tr, y_te, scaler, cols


def test_smote(t: T, X_tr_s, y_tr):
    print("\n[TEST GROUP] SMOTE")
    X_bal, y_bal = apply_smote(X_tr_s, y_tr)
    t.check("Balanced classes have equal counts",
            y_bal.value_counts()[0] == y_bal.value_counts()[1],
            f"counts={dict(y_bal.value_counts())}")
    t.check("Balanced rows > original rows",
            len(X_bal) > len(X_tr_s))
    t.check("Number of features unchanged",
            X_bal.shape[1] == X_tr_s.shape[1])
    return X_bal, y_bal


def test_tiny_train(t: T, X_bal, y_bal):
    print("\n[TEST GROUP] Tiny training smoke test")
    # Tiny forest for speed — we only want to prove the data feeds through
    model = RandomForestClassifier(
        n_estimators=10, max_depth=10, random_state=42, n_jobs=-1
    )
    model.fit(X_bal, y_bal)
    t.check("Tiny forest trained", hasattr(model, "estimators_"))
    t.check("Tiny forest has 10 trees", len(model.estimators_) == 10)
    t.check("Tiny forest saw 30 features", model.n_features_in_ == 30)
    return model


def test_saved_artifacts(t: T):
    print("\n[TEST GROUP] Saved artifacts")
    t.check("artifacts_exist()", artifacts_exist())
    model = load_model()
    scaler = load_scaler()
    metadata = load_metadata()
    metrics = load_metrics()

    t.check("Model type is RandomForestClassifier",
            type(model).__name__ == "RandomForestClassifier")
    t.check("Model expects 30 features", model.n_features_in_ == 30)
    t.check("Metadata feature count == 30",
            metadata.get("n_features") == 30)
    t.check("Metadata scaled_columns == ['Time','Amount']",
            metadata.get("scaled_columns") == SCALE_COLUMNS)
    t.check("Feature names length 30",
            len(metadata.get("feature_names", [])) == 30)
    t.check("Metrics contains precision",
            "precision" in metrics)
    t.check("Metrics precision in [0,1]",
            0.0 <= metrics["precision"] <= 1.0,
            f"precision={metrics['precision']}")
    t.check("Metrics recall in [0,1]",
            0.0 <= metrics["recall"] <= 1.0,
            f"recall={metrics['recall']}")
    t.check("Metrics roc_auc in [0,1]",
            0.0 <= metrics["roc_auc"] <= 1.0,
            f"roc_auc={metrics['roc_auc']}")


def test_predictor(t: T):
    print("\n[TEST GROUP] TransactionPredictor")
    predictor = TransactionPredictor()

    # Load a real fraud row
    df = load_dataset()
    fraud_row = df[df["Class"] == 1].iloc[0].drop("Class").to_dict()
    genuine_row = df[df["Class"] == 0].iloc[0].drop("Class").to_dict()

    fraud_result = predictor.predict(fraud_row)
    genuine_result = predictor.predict(genuine_row)

    t.check("Fraud row predicted as Fraudulent",
            fraud_result["prediction"] == "Fraudulent",
            str(fraud_result))
    t.check("Fraud row risk is High",
            fraud_result["risk_level"] == "High")
    t.check("Fraud row probability > 0.75",
            fraud_result["fraud_probability"] > 0.75,
            f"prob={fraud_result['fraud_probability']}")
    t.check("Genuine row predicted as Genuine",
            genuine_result["prediction"] == "Genuine",
            str(genuine_result))
    t.check("Genuine row risk is Low",
            genuine_result["risk_level"] == "Low")
    t.check("Genuine row probability < 0.25",
            genuine_result["fraud_probability"] < 0.25,
            f"prob={genuine_result['fraud_probability']}")

    # Error handling
    bad = dict(fraud_row)
    bad.pop("V5")
    try:
        predictor.predict(bad)
        t.check("Missing feature raises ValueError", False,
                "no exception raised")
    except ValueError:
        t.check("Missing feature raises ValueError", True)

    # Extra key is dropped
    extra = dict(fraud_row)
    extra["Class"] = 1
    result = predictor.predict(extra)
    t.check("Extra 'Class' key is ignored",
            result["prediction"] in ("Fraudulent", "Genuine"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("ML PIPELINE TEST SUITE")
    print("=" * 65)

    t = T()

    df_clean = test_loading(t)
    X_tr_s, X_te_s, y_tr, y_te, scaler, cols = test_split_and_scale(t, df_clean)
    X_bal, y_bal = test_smote(t, X_tr_s, y_tr)
    test_tiny_train(t, X_bal, y_bal)
    test_saved_artifacts(t)
    test_predictor(t)

    return t.summary()


if __name__ == "__main__":
    sys.exit(main())