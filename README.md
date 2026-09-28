# Credit Card Fraud Detection Using Binary Classification

> An end-to-end machine learning application that predicts whether a credit card
> transaction is **Genuine (0)** or **Fraudulent (1)** using a Random Forest
> Classifier trained on SMOTE-balanced data, served through FastAPI and consumed
> by a React dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikit-learn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Project Highlights](#project-highlights)
- [Dataset](#dataset)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Model Performance](#model-performance)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Concept Explanations](#concept-explanations)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Problem Statement

Credit card fraud costs the global economy tens of billions of dollars every
year. The challenge is not just detecting fraud — it's detecting a class that
represents less than **0.2%** of all transactions while keeping false alarms
low enough that genuine customers aren't constantly blocked.

This project builds a complete pipeline that:

1. Ingests the public **Credit Card Fraud Detection** dataset
2. Handles the severe class imbalance with **SMOTE**
3. Trains a **Random Forest** classifier
4. Evaluates it with the metrics that matter for imbalanced data
5. Exposes predictions via a **FastAPI** backend
6. Visualizes everything in a **React** dashboard

---

## Project Highlights

- **Binary classification** with a Random Forest of 100 trees
- **SMOTE** applied **only to the training set** — no data leakage
- **Stratified train/test split** preserves the fraud ratio in both sets
- **`StandardScaler` fit on training data only**
- Evaluated with **Precision, Recall, F1-score, ROC-AUC**, and full confusion matrix
- **Reusable prediction module** shared by the CLI demo and the FastAPI backend
- **Clean architecture**: preprocessing, training, evaluation, and prediction in
  separate modules
- **REST API** with Pydantic validation and CORS
- **Modern React UI** with stat cards, charts, and live predictions
- **Full test suites** for the ML pipeline, the backend API, and the frontend
- No hard-coded predictions — every result comes from the trained model

---

## Dataset

**Source:** [Kaggle — Credit Card Fraud Detection (ULB Machine Learning Group)](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)

| Property | Value |
|---|---|
| Total transactions | 284,807 |
| Genuine (Class 0) | 284,315 |
| Fraudulent (Class 1) | 492 |
| Fraud rate | **0.1727%** |
| Features | 30 (Time, V1–V28, Amount) |
| Target | `Class` (0 = Genuine, 1 = Fraud) |

**Notes on the features:**

- `V1`–`V28` are the result of a PCA transformation applied by the dataset
  authors to protect cardholder privacy. They are already standardized.
- `Time` = seconds elapsed since the first transaction in the dataset.
- `Amount` = transaction amount in the original currency.
- `Time` and `Amount` are scaled with `StandardScaler` during preprocessing.

The CSV must be placed at `dataset/creditcard.csv`. It is **not** committed to
Git (see `.gitignore`).

---

## Architecture

```
                Dataset (creditcard.csv)
                          │
                          ▼
                    Data Loading
                          │
                          ▼
                   Data Cleaning
                (remove duplicates)
                          │
                          ▼
              Exploratory Data Analysis
                          │
                          ▼
           Feature / Target Separation (X, y)
                          │
                          ▼
         Stratified Train/Test Split (80/20)
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        Training set              Test set
              │                       │
              ▼                       │
   Fit StandardScaler (train only)    │
              │                       │
              ▼                       │
      Apply SMOTE (train only)        │
              │                       │
              ▼                       │
   Random Forest Classifier           │
              │                       │
              ▼                       │
           Predict  ◄─────────────────┘
              │
              ▼
         Evaluation
   (Precision, Recall, F1, ROC-AUC,
    Confusion Matrix, Feature Importance)
              │
              ▼
      Save Model + Scaler + Metadata
              │
              ▼
         FastAPI Backend
              │
              ▼
       React Frontend
              │
              ▼
    Transaction Prediction
              │
              ▼
      Fraud / Genuine Result
```

---

## Project Structure

```
Credit-Card-Fraud-Detection/
│
├── dataset/
│   └── creditcard.csv                 # Raw dataset (gitignored)
│
├── notebooks/
│   └── fraud_detection.ipynb          # EDA and pipeline walkthrough
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py               # Load, clean, split, scale, SMOTE
│   ├── train.py                       # Train the Random Forest
│   ├── evaluate.py                    # Compute metrics and save plots
│   ├── predict.py                     # Reusable prediction module
│   ├── model_io.py                    # Load/save model, scaler, metadata
│   └── test_pipeline.py               # ML pipeline test suite
│
├── models/
│   ├── fraud_detection_model.pkl      # Trained Random Forest (gitignored)
│   ├── scaler.pkl                     # Fitted StandardScaler (gitignored)
│   ├── training_metadata.json         # Feature names, scaled columns
│   ├── metrics.json                   # Evaluation metrics
│   └── model_info.txt                 # Human-readable model summary
│
├── reports/
│   ├── class_distribution.png
│   ├── amount_distribution.png
│   ├── time_distribution.png
│   ├── correlation_heatmap.png
│   ├── smote_comparison.png
│   ├── confusion_matrix.png
│   ├── roc_curve.png
│   └── feature_importance.png
│
├── backend/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app
│   ├── schemas.py                     # Pydantic models
│   ├── test_api.py                    # API test suite (30 tests)
│   ├── test_regression.py             # Model interface regression check
│   ├── tests_manual.md                # Manual test guide for Swagger UI
│   └── requirements.txt               # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/                # Layout, StatCard, MetricBar, etc.
│   │   ├── pages/                     # Home, Predict, Performance, About
│   │   ├── services/                  # api.js, useApi.js, ToastContext
│   │   └── styles/                    # global.css + component styles
│   ├── public/
│   ├── TESTING.md                     # Frontend manual test plan
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── screenshots/                   # Screenshots for the README
│
├── requirements.txt                   # Python dependencies
├── TESTING.md                         # Master test guide
├── HOW_TO_RUN.md                      # Start-from-scratch instructions
├── TROUBLESHOOTING.md                 # Common issues and fixes
├── README.md
└── .gitignore
```

---

## Model Performance

Evaluated on the **held-out test set** (never seen during training, and never
touched by SMOTE). All numbers below come from `models/metrics.json`, which is
produced by `python src/evaluate.py`.

| Metric | Value |
|---|---|
| **Accuracy** | 0.9994 |
| **Precision** | 0.8612 |
| **Recall** | 0.8211 |
| **F1-score** | 0.8407 |
| **ROC-AUC** | 0.9752 |

### Confusion Matrix

|  | Predicted Genuine | Predicted Fraud |
|---|---|---|
| **Actual Genuine** | TN = 56,656 | FP = 11 |
| **Actual Fraud** | FN = 17 | TP = 78 |

- The model catches **78 of 95 frauds** (82.1% recall)
- Only **11 false alarms** across 56,667 genuine transactions
- ROC-AUC of **0.9752** means the model ranks a random fraud above a random
  genuine transaction 97.5% of the time

### Why these metrics and not accuracy?

Because fraud is only **0.17%** of the data. A model that predicts "genuine"
for every transaction would score **99.83% accuracy** while catching zero
fraud. Accuracy is meaningless here. Precision, Recall, F1, and ROC-AUC
are the metrics that actually tell you if a fraud detector works.

---

## Screenshots

> **Note:** Add your own screenshots here after running the app.
> Save them as PNG files in `docs/screenshots/` and update the paths below.

| Page | Screenshot |
|---|---|
| Dashboard | `docs/screenshots/dashboard.png` |
| Predict (Fraud example) | `docs/screenshots/predict_fraud.png` |
| Predict (Genuine example) | `docs/screenshots/predict_genuine.png` |
| Performance | `docs/screenshots/performance.png` |
| About | `docs/screenshots/about.png` |
| Swagger UI | `docs/screenshots/swagger.png` |

### How to capture screenshots on Windows

1. Open the page in your browser at **http://localhost:5173**
2. Press **Windows + Shift + S** to open Snipping Tool
3. Drag to select the browser area
4. The screenshot is copied to clipboard — paste into Paint or directly
   save with **Ctrl + S** into `docs/screenshots/`

---

## Tech Stack

### Machine Learning
- **Python 3.10+**
- **Pandas, NumPy** — data manipulation
- **scikit-learn** — Random Forest, scaling, metrics
- **imbalanced-learn** — SMOTE
- **Matplotlib, Seaborn** — charts and plots
- **Joblib** — model persistence

### Backend
- **FastAPI** — REST framework
- **Uvicorn** — ASGI server
- **Pydantic** — request/response validation

### Frontend
- **React 18** — UI
- **Vite** — build tool and dev server
- **React Router** — client-side routing
- **Axios** — HTTP client
- **Recharts** — charts
- **React Icons** — icon library

---

## Installation

### Prerequisites

- **Windows 10/11** (instructions assume PowerShell)
- **Python 3.10 or newer** — [python.org](https://www.python.org/downloads/)
- **Node.js 18 or newer** — [nodejs.org](https://nodejs.org/)
- **VS Code** — [code.visualstudio.com](https://code.visualstudio.com/)
- The **Jupyter** extension for VS Code (for the notebook)
- The **Python** extension for VS Code

### 1. Clone or download the project

```powershell
cd $env:USERPROFILE\Desktop
git clone <your-repo-url> Credit-Card-Fraud-Detection
cd Credit-Card-Fraud-Detection
```

(Or download the ZIP and extract it.)

### 2. Download the dataset

Download `creditcard.csv` from
[Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) and place
it at:

```
dataset/creditcard.csv
```

### 3. Create the Python environment

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

---

## How to Run

You need **three terminals** in VS Code.

### Terminal 1 — Train and evaluate the model

```powershell
venv\Scripts\activate
python src\train.py
python src\evaluate.py
```

This produces `models/*.pkl`, `models/*.json`, and `reports/*.png`.

### Terminal 2 — Start the FastAPI backend

```powershell
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

API live at: **http://127.0.0.1:8000**
Swagger UI: **http://127.0.0.1:8000/docs**

### Terminal 3 — Start the React frontend

```powershell
cd frontend
npm run dev
```

Dashboard live at: **http://localhost:5173**

Full walkthrough in [`HOW_TO_RUN.md`](HOW_TO_RUN.md).

---

## Testing

Three test suites cover the whole stack.

### ML pipeline test

```powershell
python src\test_pipeline.py
```

Verifies data loading, cleaning, split, scaling, SMOTE, the saved model, and
the prediction module. Expected: **40/40 tests passed**.

### Backend API test

With the backend running:

```powershell
python backend\test_api.py
```

Hits every endpoint and asserts on the response shape and content. Expected:
**30/30 tests passed**.

### Model regression test

```powershell
python backend\test_regression.py
```

Ensures the model interface (feature order, count, scaled columns) hasn't
drifted. Expected: **REGRESSION TESTS PASSED**.

### Frontend manual test

Open [`frontend/TESTING.md`](frontend/TESTING.md) and walk through the
checklist.

Full guide in [`TESTING.md`](TESTING.md).

---

## API Reference

Base URL during development: `http://127.0.0.1:8000`

### `GET /`

Returns a status message.

```json
{
  "status": "ok",
  "message": "Credit Card Fraud Detection API is running.",
  "version": "1.0.0"
}
```

### `GET /health`

Liveness probe.

```json
{ "status": "healthy" }
```

### `POST /predict`

Predict a single transaction. Body must include all 30 features.

**Request body:**

```json
{
  "Time": 0.0,
  "V1": -1.3598071336738,
  "V2": -0.0727811733098497,
  "...": "...",
  "V28": -0.0210530534538215,
  "Amount": 149.62
}
```

**Response (fraud):**

```json
{
  "prediction": "Fraudulent",
  "class": 1,
  "fraud_probability": 0.98,
  "risk_level": "High",
  "threshold_used": 0.5
}
```

**Response (genuine):**

```json
{
  "prediction": "Genuine",
  "class": 0,
  "fraud_probability": 0.0,
  "risk_level": "Low",
  "threshold_used": 0.5
}
```

### `POST /predict/batch`

Body:

```json
{ "transactions": [ { ... }, { ... } ] }
```

Response:

```json
{
  "count": 2,
  "results": [ { ... }, { ... } ]
}
```

### `GET /metrics`

Returns `models/metrics.json`.

### `GET /model-info`

Returns the training metadata, a plain-text summary, and cached dataset
statistics:

```json
{
  "metadata": { "feature_names": [...], "n_features": 30, ... },
  "summary": "=== MODEL SUMMARY ===\n...",
  "dataset_stats": {
    "total_transactions": 283726,
    "fraud_cases": 473,
    "genuine_cases": 283253,
    "fraud_percentage": 0.1667,
    "raw_rows": 284807
  }
}
```

### `GET /reports`

Lists available report images.

### `GET /reports/{filename}`

Serves a report image (PNG).

---

## Concept Explanations

### What is binary classification?

A task where the model chooses between **two classes**. Here:
`0 = Genuine`, `1 = Fraud`.

### What is class imbalance?

When one class is far more common than the other. Here, fraud is
approximately **0.17%** of transactions. Standard accuracy becomes
misleading.

### Why is SMOTE needed?

Without balancing, a model can minimize loss by predicting the majority
class almost always. SMOTE (**S**ynthetic **M**inority **O**versampling
**TE**chnique) generates new minority-class samples by interpolating between
real fraud examples and their nearest fraud neighbors. The model then sees a
**balanced** training set.

### Why apply SMOTE only to training data?

If SMOTE were applied before the split:

1. Synthetic fraud rows would leak into the test set — you'd be testing on
   fake data.
2. Real fraud rows would appear nearly duplicated in both sets — the test
   set would no longer represent unseen transactions.

**Rule:** anything that *learns* from data (scalers, SMOTE) must fit on the
training set only. The test set is transformed with those learned objects,
never re-fit.

### What is a Random Forest?

An ensemble of decision trees. Each tree is trained on a random subset of
rows and features. They vote, and the majority wins. Averaging across many
trees cancels out individual mistakes, giving a stronger model than any
single tree.

### Precision vs Recall

- **Precision** = of all transactions we *flagged as fraud*, how many really
  were fraud? High precision means few false alarms.
- **Recall** = of all *actual frauds*, how many did we catch? High recall
  means we miss fewer frauds.

There's a trade-off. In fraud detection, we usually prefer high recall
(catch frauds) even if precision drops a bit (some false alarms).

### What is a confusion matrix?

A 2×2 table showing TP, TN, FP, FN. It reveals the *type* of mistakes the
model makes:

- **FP** = we flagged a genuine transaction as fraud (customer annoyance)
- **FN** = we missed a real fraud (money lost)

### What is ROC-AUC?

ROC = Receiver Operating Characteristic. It plots True Positive Rate against
False Positive Rate at every possible threshold. AUC = area under that curve.
It equals the probability that the model ranks a random fraud above a random
genuine transaction. **0.5** = random, **1.0** = perfect.

### Why not use accuracy?

Because fraud is 0.17% of the data. Predicting "genuine" every time gives
99.83% accuracy but catches zero fraud. Accuracy tells you nothing useful
about a fraud detector.

### What is FastAPI?

A modern Python web framework. It uses **Pydantic** for automatic request
validation and generates interactive documentation (Swagger UI) for free.
It's fast, type-safe, and beginner-friendly.

### How does React talk to FastAPI?

Via HTTP. The React app uses **Axios** to `POST` a transaction to
`/predict`. Vite's dev server proxies `/api/*` requests to
`http://127.0.0.1:8000`. FastAPI receives the JSON, validates it with
Pydantic, calls the model, and returns a JSON response that React renders
into cards and toasts.

### How does the saved model make predictions?

- **Training** produces a `.pkl` file containing the fitted Random Forest
  and a `.pkl` for the fitted `StandardScaler`.
- **The backend** loads both once at startup and keeps them in memory.
- **On each request**, the backend scales the incoming `Time` and `Amount`
  using the *same* scaler, arranges the features in the exact order the
  model was trained on, and calls `model.predict_proba`.
- The class with the higher probability wins; the fraud probability is
  returned to the client.

---

## Roadmap

Ideas for future versions:

- [ ] Compare Random Forest with XGBoost and Logistic Regression
- [ ] Add hyperparameter tuning (GridSearchCV) as an optional script
- [ ] Introduce SHAP for per-transaction feature attributions
- [ ] Add a batch prediction UI that accepts CSV uploads
- [ ] Add authentication to the API
- [ ] Deploy backend to Render / Railway and frontend to Vercel
- [ ] Add a Docker Compose setup for one-command startup
- [ ] Serve a live "streaming" view of recent predictions

---

## License

This project is released under the **MIT License**. You are free to use,
modify, and distribute it with attribution.

The dataset is provided by the **ULB Machine Learning Group** and is subject
to its own terms on Kaggle.

---

## Acknowledgements

- **ULB Machine Learning Group** and **Worldline** for publishing the
  Credit Card Fraud Detection dataset
- **Kaggle** for hosting it
- The maintainers of **scikit-learn**, **imbalanced-learn**, **FastAPI**,
  **React**, and **Vite**
- **Chawla et al. (2002)** — original SMOTE paper
- **Breiman (2001)** — Random Forests

---

## Author

**Your Name**
Course / University
[your.email@example.com](mailto:your.email@example.com)

---

*Built as a learning project to demonstrate an end-to-end machine learning
workflow — from raw CSV to a working web application.*