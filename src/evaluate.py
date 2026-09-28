"""
evaluate.py
-----------
Evaluate the trained Random Forest on the untouched test set.

Outputs
-------
reports/confusion_matrix.png
reports/roc_curve.png
reports/feature_importance.png
models/metrics.json
models/model_info.txt (refreshed with metrics)

Run from the project root:
    python src/evaluate.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from preprocessing import (
    REPORTS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    load_dataset,
    clean_dataset,
    separate_features_target,
    split_data,
)

from model_io import (
    load_model,
    load_scaler,
    load_metadata,
    save_metrics,
    save_model_info,
)


# ---------------------------------------------------------------------------
# Data + artifacts
# ---------------------------------------------------------------------------
def load_artifacts():
    """Load model, scaler, and metadata from disk via model_io."""
    model = load_model()
    scaler = load_scaler()
    metadata = load_metadata()
    print(f"[load_artifacts] Model  : {type(model).__name__}")
    print(f"[load_artifacts] Trees  : {len(model.estimators_)}")
    print(f"[load_artifacts] Features: {model.n_features_in_}")
    return model, scaler, metadata


def rebuild_test_set(scaler, metadata):
    """
    Recreate the exact same test split used during training and apply the
    scaler fitted during training.
    """
    print("\n[rebuild_test_set] Rebuilding the test set from scratch...")
    df = clean_dataset(load_dataset())
    X, y = separate_features_target(df)

    _, X_test, _, y_test = split_data(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    scaled_columns = metadata["scaled_columns"]
    X_test = X_test.copy()
    X_test[scaled_columns] = scaler.transform(X_test[scaled_columns])

    # Ensure column order matches training
    X_test = X_test[metadata["feature_names"]]

    print(f"[rebuild_test_set] X_test: {X_test.shape}, y_test: {y_test.shape}")
    return X_test, y_test


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(y_test, y_pred, y_proba) -> dict:
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "accuracy":         float((tp + tn) / (tp + tn + fp + fn)),
        "precision":        float(precision_score(y_test, y_pred, zero_division=0)),
        "recall":           float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score":         float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc":          float(roc_auc_score(y_test, y_proba)),
        "true_positives":   int(tp),
        "true_negatives":   int(tn),
        "false_positives":  int(fp),
        "false_negatives":  int(fn),
        "test_set_size":    int(len(y_test)),
        "actual_frauds":    int((y_test == 1).sum()),
        "predicted_frauds": int((y_pred == 1).sum()),
    }
    return metrics


def print_metrics(metrics: dict) -> None:
    line = "=" * 60
    print("\n" + line)
    print("MODEL EVALUATION RESULTS")
    print(line)
    print(f"Test set size        : {metrics['test_set_size']:,}")
    print(f"Actual frauds        : {metrics['actual_frauds']:,}")
    print(f"Predicted frauds     : {metrics['predicted_frauds']:,}")
    print("-" * 60)
    print(f"Accuracy             : {metrics['accuracy']:.4f}")
    print(f"Precision            : {metrics['precision']:.4f}")
    print(f"Recall               : {metrics['recall']:.4f}")
    print(f"F1-score             : {metrics['f1_score']:.4f}")
    print(f"ROC-AUC              : {metrics['roc_auc']:.4f}")
    print("-" * 60)
    print("Confusion Matrix (raw counts):")
    print(f"  True Negatives  (TN): {metrics['true_negatives']:,}")
    print(f"  False Positives (FP): {metrics['false_positives']:,}")
    print(f"  False Negatives (FN): {metrics['false_negatives']:,}")
    print(f"  True Positives  (TP): {metrics['true_positives']:,}")
    print(line + "\n")


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------
def plot_confusion_matrix(y_test, y_pred) -> Path:
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm, annot=True, fmt=",d", cmap="Blues", cbar=True,
        xticklabels=["Predicted Genuine", "Predicted Fraud"],
        yticklabels=["Actual Genuine", "Actual Fraud"],
        annot_kws={"size": 13, "weight": "bold"},
    )
    plt.title("Confusion Matrix", fontsize=14, fontweight="bold")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    out = REPORTS_DIR / "confusion_matrix.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot_confusion_matrix] Saved -> {out}")
    return out


def plot_roc_curve(y_test, y_proba) -> Path:
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, color="#2E86AB", lw=2, label=f"ROC curve (AUC = {auc:.4f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Random guess")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate (Recall)")
    plt.title("ROC Curve", fontsize=14, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = REPORTS_DIR / "roc_curve.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot_roc_curve] Saved -> {out}")
    return out


def plot_feature_importance(model, feature_names) -> Path:
    importances = model.feature_importances_
    order = np.argsort(importances)[::-1]
    top_idx = order[:15]

    plt.figure(figsize=(10, 7))
    sns.barplot(
        x=importances[top_idx],
        y=[feature_names[i] for i in top_idx],
        color="#2E86AB",
    )
    plt.title("Top 15 Feature Importances (Random Forest)",
              fontsize=14, fontweight="bold")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    out = REPORTS_DIR / "feature_importance.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[plot_feature_importance] Saved -> {out}")
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 65)
    print("CREDIT CARD FRAUD DETECTION - MODEL EVALUATION")
    print("=" * 65)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load
    model, scaler, metadata = load_artifacts()

    # 2. Test set
    X_test, y_test = rebuild_test_set(scaler, metadata)

    # 3. Predict
    print("\n[evaluate] Generating predictions...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # 4. Metrics
    metrics = compute_metrics(y_test, y_pred, y_proba)
    print_metrics(metrics)

    print("Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=["Genuine (0)", "Fraud (1)"],
        digits=4, zero_division=0,
    ))

    # 5. Plots
    print("[evaluate] Generating plots...")
    plot_confusion_matrix(y_test, y_pred)
    plot_roc_curve(y_test, y_proba)
    plot_feature_importance(model, metadata["feature_names"])

    # 6. Persist metrics + refresh model_info
    print("\n[save] Persisting metrics via model_io...")
    save_metrics(metrics)
    save_model_info(model, metadata, metrics=metrics)

    print("\n" + "=" * 65)
    print("EVALUATION COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()