"""
test_regression.py
------------------
Checks the saved model and metadata against the interface the FastAPI
backend assumes. If training is retrained with different column order
or a different number of features, this test fails loudly.

Run from the project root:
    python backend/test_regression.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from model_io import (  # noqa: E402
    MODEL_PATH, SCALER_PATH, METADATA_PATH, METRICS_PATH,
    load_model, load_metadata,
)
from preprocessing import SCALE_COLUMNS, TARGET_COLUMN  # noqa: E402


EXPECTED_FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def main() -> int:
    print("=" * 65)
    print("REGRESSION TEST - Model interface")
    print("=" * 65)

    ok = True

    # ---- Files exist ----
    for label, path in [
        ("Model", MODEL_PATH),
        ("Scaler", SCALER_PATH),
        ("Metadata", METADATA_PATH),
        ("Metrics", METRICS_PATH),
    ]:
        exists = path.exists()
        print(f"[{'OK' if exists else 'XX'}] {label:<10} {path}")
        ok = ok and exists

    if not ok:
        print("\nMissing artifacts. Run 'python src/train.py' and 'python src/evaluate.py'.")
        return 1

    model = load_model()
    metadata = load_metadata()

    # ---- Feature order ----
    feature_names = metadata["feature_names"]
    if feature_names == EXPECTED_FEATURES:
        print(f"[OK] Feature order matches expected 30-column layout")
    else:
        print(f"[XX] Feature order mismatch")
        print(f"     expected: {EXPECTED_FEATURES}")
        print(f"     got     : {feature_names}")
        ok = False

    # ---- Feature count ----
    if metadata["n_features"] == 30 and model.n_features_in_ == 30:
        print(f"[OK] Model expects 30 features")
    else:
        print(f"[XX] Model feature count mismatch: "
              f"metadata={metadata['n_features']}, model={model.n_features_in_}")
        ok = False

    # ---- Scaled columns ----
    if metadata["scaled_columns"] == SCALE_COLUMNS:
        print(f"[OK] Scaled columns == {SCALE_COLUMNS}")
    else:
        print(f"[XX] Scaled columns mismatch: {metadata['scaled_columns']}")
        ok = False

    # ---- Target column ----
    if metadata.get("target_column") == TARGET_COLUMN:
        print(f"[OK] Target column == '{TARGET_COLUMN}'")
    else:
        print(f"[XX] Target column mismatch: {metadata.get('target_column')}")
        ok = False

    # ---- Model type ----
    if type(model).__name__ == "RandomForestClassifier":
        print(f"[OK] Model class is RandomForestClassifier")
    else:
        print(f"[XX] Model class mismatch: {type(model).__name__}")
        ok = False

    print("\n" + "=" * 65)
    if ok:
        print("REGRESSION TESTS PASSED")
        return 0
    print("REGRESSION TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())