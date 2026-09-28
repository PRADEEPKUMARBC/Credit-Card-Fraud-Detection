"""
train.py
--------
End-to-end training pipeline for the Credit Card Fraud Detection model.

Steps
-----
1. Load the dataset
2. Clean (drop duplicates)
3. Separate features and target
4. Stratified train/test split
5. Fit StandardScaler on training data, apply to both
6. Apply SMOTE to the training set only
7. Train a Random Forest Classifier
8. Generate predictions and probabilities on the test set
9. Save model artifacts via model_io

Run from the project root:
    python src/train.py
"""

import time

from sklearn.ensemble import RandomForestClassifier

from preprocessing import (
    MODELS_DIR,
    RANDOM_STATE,
    load_dataset,
    clean_dataset,
    separate_features_target,
    split_data,
    fit_and_apply_scaler,
    apply_smote,
)

from model_io import (
    save_model,
    save_scaler,
    save_metadata,
    save_model_info,
)


def build_random_forest() -> RandomForestClassifier:
    """Create a Random Forest Classifier with sensible defaults."""
    return RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight=None,
        verbose=1,
    )


def train_model(X_train, y_train) -> RandomForestClassifier:
    """Fit a Random Forest classifier on the provided training data."""
    print("\n[train_model] Building Random Forest...")
    model = build_random_forest()

    print("[train_model] Training started. This may take 30s - 2 minutes.\n")
    t0 = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - t0

    print(f"\n[train_model] Training complete in {elapsed:.2f} seconds.")
    print(f"[train_model] Trees trained: {len(model.estimators_)}")
    print(f"[train_model] Number of features seen: {model.n_features_in_}")
    return model


def main() -> None:
    """Run the full training pipeline."""
    print("=" * 65)
    print("CREDIT CARD FRAUD DETECTION - TRAINING PIPELINE")
    print("=" * 65)

    # 1. Load
    print("\n[1/7] Loading dataset...")
    df_raw = load_dataset()
    print(f"      Raw shape: {df_raw.shape}")

    # 2. Clean
    print("\n[2/7] Cleaning dataset (dropping duplicates)...")
    df = clean_dataset(df_raw)

    # 3. Features / target
    print("\n[3/7] Separating features and target...")
    X, y = separate_features_target(df)

    # 4. Split
    print("\n[4/7] Stratified train/test split...")
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 5. Scale
    print("\n[5/7] Fitting scaler on training data and applying to both...")
    X_train_scaled, X_test_scaled, scaler, scaled_cols = fit_and_apply_scaler(
        X_train, X_test
    )

    # 6. SMOTE
    print("\n[6/7] Applying SMOTE to training data only...")
    X_train_bal, y_train_bal = apply_smote(X_train_scaled, y_train)

    # 7. Train
    print("\n[7/7] Training Random Forest...")
    model = train_model(X_train_bal, y_train_bal)

    # Sanity predictions
    print("\n[train_model] Generating sanity-check predictions on test set...")
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    print(f"[train_model] Predicted frauds on test set: {int(y_pred.sum())}")
    print(f"[train_model] Actual frauds on test set   : {int(y_test.sum())}")
    print(f"[train_model] Probability array shape     : {y_proba.shape}")

    # Build metadata
    feature_names = list(X_test_scaled.columns)
    metadata = {
        "scaled_columns": scaled_cols,
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "target_column": "Class",
        "model_type": "RandomForestClassifier",
        "random_state": RANDOM_STATE,
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
    }

    # Save everything through model_io
    print("\n[save] Persisting artifacts via model_io...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    save_model(model)
    save_scaler(scaler)
    save_metadata(metadata)

    # Write a human-readable summary (metrics filled in later by evaluate.py)
    save_model_info(model, metadata, metrics=None)

    print("\n" + "=" * 65)
    print("TRAINING PIPELINE COMPLETE")
    print("=" * 65)
    print("Next: run 'python src/evaluate.py' to compute metrics and plots.")
    print("=" * 65)


if __name__ == "__main__":
    main()