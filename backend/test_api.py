"""
test_api.py
-----------
Automated test suite for the Credit Card Fraud Detection FastAPI backend.

Requires the server to already be running:
    uvicorn backend.main:app --reload --port 8000

Run from the project root:
    python backend/test_api.py
"""

from __future__ import annotations

import json
import sys
import time
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10  # seconds


# ---------------------------------------------------------------------------
# Test payloads (real rows from the dataset)
# ---------------------------------------------------------------------------
FRAUD_EXAMPLE: dict[str, float] = {
    "Time": 406.0,
    "V1": -2.3122265423263, "V2": 1.95199201064158, "V3": -1.60985073229769,
    "V4": 3.9979055875468, "V5": -0.522187864667764, "V6": -1.42654531920595,
    "V7": -2.53738730624579, "V8": 1.39165724829804, "V9": -2.77008927719433,
    "V10": -2.77227214465915, "V11": 3.20203320709635, "V12": -2.89990738849473,
    "V13": -0.595221881324605, "V14": -4.28925378244217, "V15": 0.389724120274487,
    "V16": -1.14074717980657, "V17": -2.83005567450437, "V18": -0.0168224681808257,
    "V19": 0.416955705037907, "V20": 0.126910559061474, "V21": 0.517232370861764,
    "V22": -0.0350493686052974, "V23": -0.465211076182388, "V24": 0.320198198514526,
    "V25": 0.0445191674731724, "V26": 0.177839798284401, "V27": 0.261145002567677,
    "V28": -0.143275874698919, "Amount": 0.0,
}

GENUINE_EXAMPLE: dict[str, float] = {
    "Time": 0.0,
    "V1": -1.3598071336738, "V2": -0.0727811733098497, "V3": 2.53634673796914,
    "V4": 1.37815522427443, "V5": -0.338320769942518, "V6": 0.462387777762292,
    "V7": 0.239598554061257, "V8": 0.0986979012610507, "V9": 0.363786969611213,
    "V10": 0.0907941719789316, "V11": -0.551599533260813, "V12": -0.617800855762348,
    "V13": -0.991389847235408, "V14": -0.311169353699879, "V15": 1.46817697209427,
    "V16": -0.470400525259478, "V17": 0.207971241929242, "V18": 0.0257905801985591,
    "V19": 0.403992960255733, "V20": 0.251412098239705, "V21": -0.018306777944153,
    "V22": 0.277837575558899, "V23": -0.110473910188767, "V24": 0.0669280749146731,
    "V25": 0.128539358273528, "V26": -0.189114843888824, "V27": 0.133558376740387,
    "V28": -0.0210530534538215, "Amount": 149.62,
}


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------
class TestRunner:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.results: list[tuple[str, bool, str]] = []

    def check(
        self,
        name: str,
        condition: bool,
        detail: str = "",
    ) -> None:
        status = "PASS" if condition else "FAIL"
        marker = "[+]" if condition else "[x]"
        print(f"{marker} {status:<4} {name}")
        if detail:
            print(f"        {detail}")
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        self.results.append((name, condition, detail))

    def summary(self) -> int:
        total = self.passed + self.failed
        print("\n" + "=" * 65)
        print(f"SUMMARY: {self.passed}/{total} tests passed")
        if self.failed:
            print("\nFailed tests:")
            for name, ok, _ in self.results:
                if not ok:
                    print(f"  - {name}")
        print("=" * 65)
        return 0 if self.failed == 0 else 1


def pretty(obj: Any, max_len: int = 200) -> str:
    s = json.dumps(obj, default=str)
    return s if len(s) <= max_len else s[:max_len] + "..."


# ---------------------------------------------------------------------------
# Individual tests
# ---------------------------------------------------------------------------
def test_root(r: TestRunner) -> None:
    print("\n[TEST] GET /")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        data = resp.json()
        r.check("status code 200", resp.status_code == 200, f"got {resp.status_code}")
        r.check("status == 'ok'", data.get("status") == "ok", pretty(data))
        r.check("has version field", "version" in data)
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_health(r: TestRunner) -> None:
    print("\n[TEST] GET /health")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200)
        r.check("body has status=healthy",
                resp.json().get("status") == "healthy")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_metrics(r: TestRunner) -> None:
    print("\n[TEST] GET /metrics")
    try:
        resp = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200)
        data = resp.json()
        required = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
        r.check("has all metric keys", all(k in data for k in required),
                f"keys: {list(data.keys())}")
        # Sanity ranges
        r.check("roc_auc in [0, 1]", 0.0 <= data["roc_auc"] <= 1.0,
                f"roc_auc={data['roc_auc']}")
        r.check("precision in [0, 1]", 0.0 <= data["precision"] <= 1.0,
                f"precision={data['precision']}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_model_info(r: TestRunner) -> None:
    print("\n[TEST] GET /model-info")
    try:
        resp = requests.get(f"{BASE_URL}/model-info", timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200)
        data = resp.json()
        r.check("has 'metadata' key", "metadata" in data)
        r.check("has 'summary' key", "summary" in data)
        r.check("feature count == 30",
                data["metadata"].get("n_features") == 30,
                f"n_features={data['metadata'].get('n_features')}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_reports_list(r: TestRunner) -> None:
    print("\n[TEST] GET /reports")
    try:
        resp = requests.get(f"{BASE_URL}/reports", timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200)
        data = resp.json()
        r.check("has 'reports' key", "reports" in data)
        r.check("at least 3 PNGs available", len(data.get("reports", [])) >= 3,
                f"count={len(data.get('reports', []))}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_reports_image(r: TestRunner) -> None:
    print("\n[TEST] GET /reports/confusion_matrix.png")
    try:
        resp = requests.get(f"{BASE_URL}/reports/confusion_matrix.png",
                            timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200)
        r.check("content-type is image/png",
                resp.headers.get("content-type", "").startswith("image/png"),
                resp.headers.get("content-type", ""))
        r.check("body is not empty", len(resp.content) > 0,
                f"bytes={len(resp.content)}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_reports_missing(r: TestRunner) -> None:
    print("\n[TEST] GET /reports/does_not_exist.png  (expect 404)")
    try:
        resp = requests.get(f"{BASE_URL}/reports/does_not_exist.png",
                            timeout=TIMEOUT)
        r.check("status code 404", resp.status_code == 404)
        r.check("error field present", "error" in resp.json(),
                pretty(resp.json()))
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_predict_fraud(r: TestRunner) -> None:
    print("\n[TEST] POST /predict  (known fraud row)")
    try:
        resp = requests.post(f"{BASE_URL}/predict", json=FRAUD_EXAMPLE,
                             timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200,
                f"got {resp.status_code} body={pretty(resp.text)}")
        data = resp.json()
        r.check("prediction == 'Fraudulent'",
                data.get("prediction") == "Fraudulent", pretty(data))
        r.check("class == 1", data.get("class") == 1)
        r.check("risk_level == 'High'", data.get("risk_level") == "High")
        r.check("fraud_probability >= 0.75",
                data.get("fraud_probability", 0) >= 0.75,
                f"probability={data.get('fraud_probability')}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_predict_genuine(r: TestRunner) -> None:
    print("\n[TEST] POST /predict  (known genuine row)")
    try:
        resp = requests.post(f"{BASE_URL}/predict", json=GENUINE_EXAMPLE,
                             timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200,
                f"got {resp.status_code} body={pretty(resp.text)}")
        data = resp.json()
        r.check("prediction == 'Genuine'",
                data.get("prediction") == "Genuine", pretty(data))
        r.check("class == 0", data.get("class") == 0)
        r.check("risk_level == 'Low'", data.get("risk_level") == "Low")
        r.check("fraud_probability <= 0.25",
                data.get("fraud_probability", 1) <= 0.25,
                f"probability={data.get('fraud_probability')}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_predict_missing_field(r: TestRunner) -> None:
    print("\n[TEST] POST /predict  (missing V5 — expect 422)")
    bad = dict(GENUINE_EXAMPLE)
    del bad["V5"]
    try:
        resp = requests.post(f"{BASE_URL}/predict", json=bad, timeout=TIMEOUT)
        r.check("status code 422", resp.status_code == 422,
                f"got {resp.status_code}")
        body = resp.json()
        r.check("error mentions V5",
                "V5" in json.dumps(body),
                pretty(body))
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_predict_batch(r: TestRunner) -> None:
    print("\n[TEST] POST /predict/batch  (fraud + genuine)")
    payload = {"transactions": [FRAUD_EXAMPLE, GENUINE_EXAMPLE]}
    try:
        resp = requests.post(f"{BASE_URL}/predict/batch", json=payload,
                             timeout=TIMEOUT)
        r.check("status code 200", resp.status_code == 200,
                f"got {resp.status_code} body={pretty(resp.text)}")
        data = resp.json()
        r.check("count == 2", data.get("count") == 2)
        results = data.get("results", [])
        r.check("results list length 2", len(results) == 2)
        if len(results) == 2:
            r.check("[0] is Fraudulent", results[0]["prediction"] == "Fraudulent")
            r.check("[1] is Genuine",    results[1]["prediction"] == "Genuine")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


def test_cors_headers(r: TestRunner) -> None:
    print("\n[TEST] CORS preflight headers")
    try:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        }
        resp = requests.options(f"{BASE_URL}/predict", headers=headers,
                                timeout=TIMEOUT)
        allow_origin = resp.headers.get("access-control-allow-origin", "")
        r.check("Access-Control-Allow-Origin includes 5173",
                "5173" in allow_origin,
                f"got: {allow_origin!r}")
    except requests.RequestException as e:
        r.check("request succeeded", False, str(e))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 65)
    print("API TEST SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 65)

    # Quick reachability check
    try:
        requests.get(f"{BASE_URL}/", timeout=3)
    except requests.RequestException:
        print(f"\n[ERROR] Could not reach the API at {BASE_URL}.")
        print("Start it with:")
        print("    uvicorn backend.main:app --reload --port 8000")
        return 2

    t0 = time.time()
    runner = TestRunner()

    test_root(runner)
    test_health(runner)
    test_metrics(runner)
    test_model_info(runner)
    test_reports_list(runner)
    test_reports_image(runner)
    test_reports_missing(runner)
    test_predict_fraud(runner)
    test_predict_genuine(runner)
    test_predict_missing_field(runner)
    test_predict_batch(runner)
    test_cors_headers(runner)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.2f}s")
    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())