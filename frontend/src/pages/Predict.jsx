/**
 * Predict.jsx
 * -----------
 * Prediction workflow page.
 *
 * Flow:
 *   1. Header explains what the page does
 *   2. Form lets the user enter 30 features (or load real examples)
 *   3. When submitted, an "inference in progress" card appears
 *   4. When a result arrives, a result card animates in
 *      with a "Why this prediction?" expandable explanation
 *   5. Two follow-up actions: predict another, or view metrics
 *
 * All results come from the real FastAPI backend.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaShieldAlt,
  FaExclamationTriangle,
  FaCheckCircle,
  FaArrowRight,
  FaRedo,
  FaChartBar,
  FaLightbulb,
  FaChevronDown,
  FaChevronUp,
  FaHistory,
} from "react-icons/fa";

import PredictionForm from "../components/PredictionForm";
import ResultCard from "../components/ResultCard";
import useApi from "../services/useApi";
import { predictTransaction } from "../services/api";
import { useToast } from "../context/ToastContext";

import "../styles/components/PredictionForm.css";
import "../styles/components/ResultCard.css";
import "../styles/pages/Predict.css";

const MAX_HISTORY = 5;

export default function Predict() {
  const { data, error, loading, run, reset } = useApi(predictTransaction);
  const toast = useToast();

  const [elapsedMs, setElapsedMs] = useState(0);
  const [history, setHistory] = useState([]);
  const [showWhy, setShowWhy] = useState(false);

  const resultRef = useRef(null);
  const hasRevealedRef = useRef(false);

  // ------------------------------------------------------------------
  // Elapsed-time ticker while inference is running
  // ------------------------------------------------------------------
  useEffect(() => {
    if (!loading) {
      setElapsedMs(0);
      return;
    }
    const t0 = performance.now();
    const id = setInterval(() => {
      setElapsedMs(performance.now() - t0);
    }, 100);
    return () => clearInterval(id);
  }, [loading]);

  // ------------------------------------------------------------------
  // Reset the "why" panel whenever a new result arrives
  // ------------------------------------------------------------------
  useEffect(() => {
    setShowWhy(false);
  }, [data]);

  // ------------------------------------------------------------------
  // Submit handler
  // ------------------------------------------------------------------
  const handlePredict = useCallback(
    async (transaction) => {
      reset();
      const result = await run(transaction);

      if (!result) return;

      // Toast feedback
      if (result.class === 1) {
        toast.error(
          `Fraud detected · ${(result.fraud_probability * 100).toFixed(2)}% confidence`
        );
      } else {
        toast.success(
          `Genuine transaction · fraud probability ${(result.fraud_probability * 100).toFixed(2)}%`
        );
      }

      // Update in-session history (client-side only, no persistence)
      setHistory((prev) =>
        [
          {
            id: Date.now(),
            class: result.class,
            probability: result.fraud_probability,
            risk: result.risk_level,
          },
          ...prev,
        ].slice(0, MAX_HISTORY)
      );

      // Smooth-scroll to result on the FIRST prediction only
      if (!hasRevealedRef.current) {
        hasRevealedRef.current = true;
        setTimeout(() => {
          resultRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }, 120);
      }
    },
    [reset, run, toast]
  );

  // ------------------------------------------------------------------
  // Surface API errors as toasts
  // ------------------------------------------------------------------
  useEffect(() => {
    if (error) toast.error(error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error]);

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  return (
    <div className="predict-page">
      {/* ============================== HERO ============================== */}
      <header className="predict-hero">
        <div className="predict-hero-main">
          <div className="predict-hero-icon">
            <FaShieldAlt size={22} />
          </div>
          <div className="predict-hero-text">
            <div className="predict-hero-badge">Live Inference</div>
            <h1>Predict Transaction</h1>
            <p>
              Enter the 30 features of a credit card transaction, or load a
              real example, to predict whether it is{" "}
              <strong>Genuine (0)</strong> or <strong>Fraudulent (1)</strong>.
            </p>
          </div>
        </div>
        <div className="predict-hero-hint">
          <FaLightbulb />
          <span>
            Tip: use <strong>Load Fraud Example</strong> to see the model in
            action.
          </span>
        </div>
      </header>

      {/* ============================== RECENT PREDICTIONS ============================== */}
      {history.length > 0 && (
        <section className="predict-history" aria-label="Recent predictions">
          <div className="predict-history-label">
            <FaHistory /> Recent
          </div>
          <div className="predict-history-chips">
            {history.map((h) => (
              <span
                key={h.id}
                className={`predict-history-chip ${
                  h.class === 1 ? "fraud" : "genuine"
                }`}
                title={`${(h.probability * 100).toFixed(2)}% fraud probability`}
              >
                {h.class === 1 ? (
                  <FaExclamationTriangle />
                ) : (
                  <FaCheckCircle />
                )}
                {h.class === 1 ? "Fraud" : "Genuine"} ·{" "}
                {(h.probability * 100).toFixed(1)}%
              </span>
            ))}
          </div>
        </section>
      )}

      {/* ============================== FORM ============================== */}
      <PredictionForm onPredict={handlePredict} loading={loading} />

      {/* ============================== ERROR ============================== */}
      {error && !loading && (
        <div className="predict-error-card">
          <div className="predict-error-icon">
            <FaExclamationTriangle />
          </div>
          <div className="predict-error-text">
            <h3>Prediction failed</h3>
            <p>{error}</p>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => reset()}
          >
            <FaRedo /> Try again
          </button>
        </div>
      )}

      {/* ============================== RESULT REGION ============================== */}
      <div
        id="prediction-result"
        ref={resultRef}
        className="predict-result-region"
        aria-live="polite"
        aria-atomic="true"
      >
        {/* Loading state */}
        {loading && (
          <div className="predict-loading-card">
            <div className="predict-loading-pulse">
              <FaShieldAlt size={32} />
            </div>
            <div className="predict-loading-text">
              <h3>Running model inference…</h3>
              <p>
                Scaling <code>Time</code> and <code>Amount</code>, aligning
                features, and querying the Random Forest.
              </p>
              <div className="predict-loading-meta">
                Elapsed: <strong>{elapsedMs.toFixed(0)} ms</strong>
              </div>
            </div>
            <div className="predict-loading-steps">
              <span className="step done">Preprocess</span>
              <span className="step active">Predict</span>
              <span className="step">Return</span>
            </div>
          </div>
        )}

        {/* Empty state (before the first prediction) */}
        {!loading && !data && !error && (
          <div className="predict-empty-card">
            <div className="predict-empty-icon">
              <FaShieldAlt size={26} />
            </div>
            <h3>No prediction yet</h3>
            <p>
              Fill the form above, or click{" "}
              <strong>Load Fraud Example</strong> or{" "}
              <strong>Load Genuine Example</strong>, then press{" "}
              <strong>Predict Transaction</strong>. The result will appear
              here.
            </p>
          </div>
        )}

        {/* Result */}
        {!loading && data && (
          <>
            <ResultCard result={data} />

            {/* Why this prediction? */}
            <div className="predict-why">
              <button
                type="button"
                className="predict-why-toggle"
                onClick={() => setShowWhy((s) => !s)}
                aria-expanded={showWhy}
              >
                <FaLightbulb />
                Why this prediction?
                {showWhy ? <FaChevronUp /> : <FaChevronDown />}
              </button>

              {showWhy && (
                <div className="predict-why-body">
                  <ul>
                    <li>
                      <strong>Fraud probability:</strong>{" "}
                      {(data.fraud_probability * 100).toFixed(2)}% — the
                      Random Forest's confidence that this transaction is
                      fraudulent.
                    </li>
                    <li>
                      <strong>Decision threshold:</strong>{" "}
                      {data.threshold_used ?? 0.5} — the probability above
                      which the model labels a transaction as fraud.
                    </li>
                    <li>
                      <strong>Risk level:</strong> {data.risk_level} — derived
                      from the probability (High ≥ 0.75, Medium ≥ 0.40,
                      otherwise Low).
                    </li>
                    <li>
                      <strong>Note:</strong> this prediction is based on the
                      exact 30 features you supplied. Changing even one
                      feature can alter the result.
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* Follow-up actions */}
            <div className="predict-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  reset();
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              >
                <FaRedo /> Predict another
              </button>
              <Link to="/performance" className="btn btn-primary">
                <FaChartBar /> View model metrics <FaArrowRight />
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}