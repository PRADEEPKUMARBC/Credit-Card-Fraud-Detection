"""
preprocessing.py
----------------
Reusable functions for loading, inspecting, cleaning, splitting, scaling,
and balancing the Credit Card Fraud Detection dataset.

Stage 2 : load_dataset(), inspect_dataset(), class_balance_report()
Stage 3 : clean_dataset(), separate_features_target(), build_scaler(), scale_columns()
Stage 4 : split_data(), fit_and_apply_scaler(), apply_smote()
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE


# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "dataset" / "creditcard.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
MODELS_DIR = PROJECT_ROOT / "models"


# ---------------------------------------------------------------------------
# Column configuration
# ---------------------------------------------------------------------------
TARGET_COLUMN = "Class"
SCALE_COLUMNS = ["Time", "Amount"]

# Reproducibility seed used everywhere
RANDOM_STATE = 42

# Test set proportion
TEST_SIZE = 0.2


# ---------------------------------------------------------------------------
# Stage 2: Loading and inspection
# ---------------------------------------------------------------------------
def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load the credit card fraud dataset from CSV."""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Dataset not found at: {path}\n"
            "Download 'creditcard.csv' from Kaggle and place it in dataset/.\n"
            "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
        )
    return pd.read_csv(path)


def inspect_dataset(df: pd.DataFrame) -> None:
    """Print a compact inspection report."""
    line = "=" * 65
    print(line)
    print("DATASET INSPECTION")
    print(line)

    print(f"\n[Shape] Rows: {df.shape[0]:,}  |  Columns: {df.shape[1]}")

    print("\n[Columns]")
    print(list(df.columns))

    print("\n[Data Types]")
    print(df.dtypes)

    print("\n[Missing Values]")
    missing = df.isnull().sum()
    total_missing = int(missing.sum())
    if total_missing == 0:
        print("No missing values found. Dataset is complete.")
    else:
        print(missing[missing > 0])
        print(f"Total missing cells: {total_missing}")

    print(f"\n[Duplicate Rows] {int(df.duplicated().sum()):,}")

    print("\n[Descriptive Statistics]")
    print(df[["Time", "Amount", "Class"]].describe().T)

    print("\n" + line)


def class_balance_report(df: pd.DataFrame, target_col: str = TARGET_COLUMN) -> pd.DataFrame:
    """Return class counts and percentages as a tidy dataframe."""
    counts = df[target_col].value_counts().sort_index()
    percentages = (counts / counts.sum() * 100).round(4)
    summary = pd.DataFrame({"count": counts, "percentage": percentages})
    summary.index.name = target_col
    return summary


# ---------------------------------------------------------------------------
# Stage 3: Cleaning and preparation
# ---------------------------------------------------------------------------
def clean_dataset(df: pd.DataFrame, drop_duplicates: bool = True) -> pd.DataFrame:
    """Drop exact duplicate rows and reset index."""
    cleaned = df.copy()
    rows_before = len(cleaned)

    if drop_duplicates:
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        print(f"[clean_dataset] Removed {rows_before - len(cleaned):,} duplicate rows.")
    else:
        print("[clean_dataset] Duplicate removal skipped.")

    print(f"[clean_dataset] Final shape: {cleaned.shape}")
    return cleaned


def separate_features_target(
    df: pd.DataFrame, target_col: str = TARGET_COLUMN
) -> tuple[pd.DataFrame, pd.Series]:
    """Split dataframe into features (X) and target (y)."""
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found.")
    X = df.drop(columns=[target_col]).copy()
    y = df[target_col].copy()
    print(f"[separate_features_target] X shape: {X.shape}, y shape: {y.shape}")
    print(f"[separate_features_target] Target classes: {sorted(y.unique().tolist())}")
    return X, y


def build_scaler() -> StandardScaler:
    """Create a fresh, unfitted StandardScaler."""
    return StandardScaler()


def scale_columns(X: pd.DataFrame) -> list[str]:
    """Return the columns that should be scaled, filtered to those present."""
    return [c for c in SCALE_COLUMNS if c in X.columns]


# ---------------------------------------------------------------------------
# Stage 4: Split, scale, balance
# ---------------------------------------------------------------------------
def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Perform a stratified train/test split.

    Stratification preserves the class ratio in both subsets, so the test
    set contains roughly the same ~0.17% fraud rate as the full dataset.

    Returns
    -------
    X_train, X_test, y_train, y_test : tuple
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,   # critical for imbalanced data
    )

    print("[split_data] Stratified train/test split completed.")
    print(f"[split_data] X_train: {X_train.shape}, y_train: {y_train.shape}")
    print(f"[split_data] X_test : {X_test.shape}, y_test : {y_test.shape}")
    print(f"[split_data] Fraud in y_train: {int(y_train.sum()):,} "
          f"({y_train.mean() * 100:.4f}%)")
    print(f"[split_data] Fraud in y_test : {int(y_test.sum()):,} "
          f"({y_test.mean() * 100:.4f}%)")

    return X_train, X_test, y_train, y_test


def fit_and_apply_scaler(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    columns: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler, list[str]]:
    """
    Fit a StandardScaler on the TRAINING data only, then apply the same
    scaling to both the training and test sets.

    Fitting on the full dataset would leak test statistics into training.
    We avoid that by fitting strictly on X_train.

    Parameters
    ----------
    X_train, X_test : pd.DataFrame
    columns : list[str], optional
        Columns to scale. Defaults to ['Time', 'Amount'] filtered by presence.

    Returns
    -------
    X_train_scaled, X_test_scaled : pd.DataFrame
    scaler : fitted StandardScaler
    columns : list[str] of columns that were scaled
    """
    if columns is None:
        columns = scale_columns(X_train)

    if not columns:
        print("[fit_and_apply_scaler] No columns to scale. Returning originals.")
        return X_train.copy(), X_test.copy(), build_scaler(), []

    scaler = build_scaler()

    # Fit ONLY on training data
    scaler.fit(X_train[columns])

    # Work on copies so we don't mutate the caller's dataframes
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[columns] = scaler.transform(X_train[columns])
    X_test_scaled[columns] = scaler.transform(X_test[columns])

    print(f"[fit_and_apply_scaler] Scaled columns: {columns}")
    print(f"[fit_and_apply_scaler] Scaler means:  {scaler.mean_.round(4)}")
    print(f"[fit_and_apply_scaler] Scaler scales: {scaler.scale_.round(4)}")

    return X_train_scaled, X_test_scaled, scaler, columns


def apply_smote(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = RANDOM_STATE,
    k_neighbors: int = 5,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Apply SMOTE to the TRAINING data only.

    SMOTE creates synthetic minority-class samples by interpolating between
    a minority sample and its k nearest minority neighbors. This is done
    AFTER the train/test split to avoid leaking synthetic data into the
    test set.

    Parameters
    ----------
    X_train, y_train : training data
    random_state : int, seed for reproducibility
    k_neighbors : int, number of nearest neighbors SMOTE uses

    Returns
    -------
    X_train_resampled, y_train_resampled
    """
    # Print balance before
    before_counts = y_train.value_counts().sort_index().to_dict()
    print(f"[apply_smote] Before SMOTE: {before_counts}")

    smote = SMOTE(random_state=random_state, k_neighbors=k_neighbors)
    X_res, y_res = smote.fit_resample(X_train, y_train)

    after_counts = y_res.value_counts().sort_index().to_dict()
    print(f"[apply_smote] After  SMOTE: {after_counts}")
    print(f"[apply_smote] New shape: {X_res.shape}")

    return X_res, y_res