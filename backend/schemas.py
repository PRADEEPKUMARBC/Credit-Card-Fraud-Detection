"""
schemas.py
----------
Pydantic models defining the request and response shapes for the
FastAPI backend.

The Transaction model defines the 30 features the model expects:
    Time, V1..V28, Amount

Pydantic validates every incoming request against this schema. Missing or
wrong-type fields produce a clean 422 error before any ML code runs.
"""

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class Transaction(BaseModel):
    """
    A single credit card transaction.
    All 30 features are required except the target ('Class'), which must
    NOT be sent — the whole point is to predict it.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Time": 0.0,
                "V1": -1.3598071336738,
                "V2": -0.0727811733098497,
                "V3": 2.53634673796914,
                "V4": 1.37815522427443,
                "V5": -0.338320769942518,
                "V6": 0.462387777762292,
                "V7": 0.239598554061257,
                "V8": 0.0986979012610507,
                "V9": 0.363786969611213,
                "V10": 0.0907941719789316,
                "V11": -0.551599533260813,
                "V12": -0.617800855762348,
                "V13": -0.991389847235408,
                "V14": -0.311169353699879,
                "V15": 1.46817697209427,
                "V16": -0.470400525259478,
                "V17": 0.207971241929242,
                "V18": 0.0257905801985591,
                "V19": 0.403992960255733,
                "V20": 0.251412098239705,
                "V21": -0.018306777944153,
                "V22": 0.277837575558899,
                "V23": -0.110473910188767,
                "V24": 0.0669280749146731,
                "V25": 0.128539358273528,
                "V26": -0.189114843888824,
                "V27": 0.133558376740387,
                "V28": -0.0210530534538215,
                "Amount": 149.62,
            }
        }
    )

    Time: float = Field(..., description="Seconds elapsed since first transaction")
    V1:  float
    V2:  float
    V3:  float
    V4:  float
    V5:  float
    V6:  float
    V7:  float
    V8:  float
    V9:  float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float = Field(..., description="Transaction amount")


class TransactionBatch(BaseModel):
    """A list of transactions for batch prediction."""
    transactions: list[Transaction]


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class PredictionResponse(BaseModel):
    """Response shape for a single prediction."""
    prediction: str = Field(..., description="'Fraudulent' or 'Genuine'")
    class_: int = Field(..., alias="class", description="1 = Fraud, 0 = Genuine")
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="'Low', 'Medium', or 'High'")
    threshold_used: float = Field(0.5, description="Decision threshold")

    model_config = ConfigDict(populate_by_name=True)


class BatchPredictionResponse(BaseModel):
    """Response shape for a batch prediction."""
    count: int
    results: list[PredictionResponse]


class APIStatus(BaseModel):
    """Simple status message for GET /."""
    status: str
    message: str
    version: str


class MetricsResponse(BaseModel):
    """Model evaluation metrics loaded from models/metrics.json."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    test_set_size: int
    actual_frauds: int
    predicted_frauds: int