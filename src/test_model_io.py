"""
Temporary verification of Stage 7 model_io module.
Delete after verification.
"""

from model_io import (
    load_model, load_scaler, load_metadata, load_metrics,
    artifacts_exist,
    MODEL_PATH, SCALER_PATH, METADATA_PATH, METRICS_PATH, INFO_PATH,
)

print("=" * 60)
print("MODEL_IO VERIFICATION")
print("=" * 60)

print("\nFile existence check:")
for label, path in [
    ("Model",     MODEL_PATH),
    ("Scaler",    SCALER_PATH),
    ("Metadata",  METADATA_PATH),
    ("Metrics",   METRICS_PATH),
    ("Model info", INFO_PATH),
]:
    exists = "YES" if path.exists() else "NO "
    size = f"{path.stat().st_size:>12,} bytes" if path.exists() else ""
    print(f"  [{exists}] {label:<10} {size}  {path.name}")

print(f"\nartifacts_exist(): {artifacts_exist()}")

print("\nLoading artifacts...")
model = load_model()
scaler = load_scaler()
metadata = load_metadata()
metrics = load_metrics()

print(f"  Model type        : {type(model).__name__}")
print(f"  Trees             : {len(model.estimators_)}")
print(f"  Features expected : {model.n_features_in_}")
print(f"  Scaled columns    : {metadata['scaled_columns']}")
print(f"  Feature count     : {metadata['n_features']}")
print(f"  ROC-AUC (metrics) : {metrics['roc_auc']:.4f}")
print(f"  Recall (metrics)  : {metrics['recall']:.4f}")

print("\nAll artifacts loaded successfully.")
print("=" * 60)