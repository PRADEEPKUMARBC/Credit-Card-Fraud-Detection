"""
main.py
-------
FastAPI backend for the Credit Card Fraud Detection project.

Endpoints
---------
GET  /                          : API status
POST /predict                   : Predict a single transaction
POST /predict/batch             : Predict many transactions at once
GET  /metrics                   : Return model evaluation metrics
GET  /model-info                : Return trained model summary + dataset stats
GET  /reports/{filename}        : Serve generated report images
GET  /reports                   : List available report images
GET  /health                    : Simple liveness probe

Run from the project root (with venv active):
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Make src/ importable so we can reuse the ML logic
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from predict import TransactionPredictor                     # noqa: E402
from model_io import METRICS_PATH, METADATA_PATH, INFO_PATH  # noqa: E402
from preprocessing import REPORTS_DIR, load_dataset, clean_dataset  # noqa: E402
from backend.schemas import (                                # noqa: E402
    APIStatus,
    BatchPredictionResponse,
    MetricsResponse,
    PredictionResponse,
    Transaction,
    TransactionBatch,
)


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
API_VERSION = "1.0.0"

app = FastAPI(
    title="Credit Card Fraud Detection API",
    description=(
        "Binary classification API that predicts whether a credit card "
        "transaction is Genuine (0) or Fraudulent (1). "
        "Model: Random Forest Classifier trained on SMOTE-balanced data."
    ),
    version=API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup: load the predictor + cache dataset stats
# ---------------------------------------------------------------------------
print("[startup] Loading predictor...")
predictor = TransactionPredictor()
print("[startup] Predictor ready.")


def _compute_dataset_stats() -> dict:
    """
    Read the raw dataset once and compute summary counts for the dashboard.
    Called at startup; the result is cached in DATASET_STATS.
    """
    try:
        df_raw = load_dataset()
        df = clean_dataset(df_raw)
        total = int(len(df))
        fraud = int((df["Class"] == 1).sum())
        genuine = int((df["Class"] == 0).sum())
        stats = {
            "total_transactions": total,
            "fraud_cases": fraud,
            "genuine_cases": genuine,
            "fraud_percentage": round(fraud / total * 100, 4),
            "raw_rows": int(len(df_raw)),
        }
        print(f"[startup] Dataset stats cached: {stats}")
        return stats
    except Exception as e:
        print(f"[startup] Could not compute dataset stats: {e}")
        return {
            "total_transactions": 0,
            "fraud_cases": 0,
            "genuine_cases": 0,
            "fraud_percentage": 0.0,
            "raw_rows": 0,
        }


DATASET_STATS = _compute_dataset_stats()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/", response_model=APIStatus, tags=["Status"])
def root() -> APIStatus:
    return APIStatus(
        status="ok",
        message="Credit Card Fraud Detection API is running.",
        version=API_VERSION,
    )


@app.get("/health", tags=["Status"])
def health() -> dict:
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_single(transaction: Transaction) -> PredictionResponse:
    try:
        txn_dict = transaction.model_dump()
        result = predictor.predict(txn_dict)
        return PredictionResponse(
            prediction=result["prediction"],
            class_=result["class"],
            fraud_probability=result["fraud_probability"],
            risk_level=result["risk_level"],
            threshold_used=result["threshold_used"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    tags=["Prediction"],
)
def predict_many(payload: TransactionBatch) -> BatchPredictionResponse:
    try:
        txns = [t.model_dump() for t in payload.transactions]
        results = predictor.predict_batch(txns)
        return BatchPredictionResponse(
            count=len(results),
            results=[
                PredictionResponse(
                    prediction=r["prediction"],
                    class_=r["class"],
                    fraud_probability=r["fraud_probability"],
                    risk_level=r["risk_level"],
                    threshold_used=r["threshold_used"],
                )
                for r in results
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {e}")


@app.get("/metrics", response_model=MetricsResponse, tags=["Model"])
def get_metrics() -> MetricsResponse:
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="metrics.json not found. Run 'python src/evaluate.py' first.",
        )
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MetricsResponse(**data)


@app.get("/model-info", tags=["Model"])
def get_model_info() -> dict:
    """
    Returns:
      - metadata: contents of training_metadata.json
      - summary : contents of model_info.txt
      - dataset_stats: cached counts for the dashboard
    """
    if not METADATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="training_metadata.json not found. Run 'python src/train.py' first.",
        )
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    info_text = ""
    if INFO_PATH.exists():
        info_text = INFO_PATH.read_text(encoding="utf-8")

    return {
        "metadata": metadata,
        "summary": info_text,
        "dataset_stats": DATASET_STATS,
    }


@app.get("/reports/{filename}", tags=["Reports"])
def get_report(filename: str):
    safe_name = Path(filename).name
    file_path = REPORTS_DIR / safe_name
    if not file_path.exists() or file_path.suffix.lower() != ".png":
        raise HTTPException(status_code=404, detail=f"Report not found: {filename}")
    return FileResponse(file_path, media_type="image/png")


@app.get("/reports", tags=["Reports"])
def list_reports() -> dict:
    if not REPORTS_DIR.exists():
        return {"reports": []}
    files = sorted(p.name for p in REPORTS_DIR.glob("*.png"))
    return {"reports": files}


if REPORTS_DIR.exists():
    app.mount(
        "/static-reports",
        StaticFiles(directory=str(REPORTS_DIR)),
        name="static-reports",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "path": str(request.url.path)},
    )