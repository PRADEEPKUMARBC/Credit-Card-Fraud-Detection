/**
 * Performance.jsx
 * ---------------
 * Model performance dashboard.
 *
 * Sections:
 *   1. Hero header with live timestamp + refresh
 *   2. Top-level metric cards (Precision, Recall, F1, ROC-AUC)
 *      with mini progress bars and interpretation hints
 *   3. Tabbed area:
 *        - "Metrics" tab -> confusion matrix + interpretation
 *        - "Charts"  tab -> embedded report PNGs in a gallery
 *   4. Empty / error / loading states handled explicitly
 *
 * Every value comes from the FastAPI backend; nothing is hard-coded.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  FaBullseye,
  FaSearchPlus,
  FaBalanceScale,
  FaChartArea,
  FaSyncAlt,
  FaThLarge,
  FaImage,
  FaExclamationTriangle,
  FaCheckCircle,
  FaArrowRight,
  FaExpand,
} from "react-icons/fa";

import StatCard from "../components/StatCard";
import ReportImage from "../components/ReportImage";
import { getMetrics } from "../services/api";
import { formatMetric as fmt } from "../services/format";

import "../styles/components/StatCard.css";
import "../styles/components/ReportImage.css";
import "../styles/pages/Performance.css";

// ---------------------------------------------------------------------------
// Metric metadata
// ---------------------------------------------------------------------------
const METRIC_CONFIG = [
  {
    key: "precision",
    label: "Precision",
    icon: <FaBullseye />,
    accent: "primary",
    hint: "Of flagged frauds, how many were real",
    describe: (v) =>
      v >= 0.9
        ? "Excellent — very few false alarms."
        : v >= 0.75
        ? "Good — a small number of false alarms."
        : "Consider raising the decision threshold.",
  },
  {
    key: "recall",
    label: "Recall",
    icon: <FaSearchPlus />,
    accent: "success",
    hint: "Of real frauds, how many we caught",
    describe: (v) =>
      v >= 0.9
        ? "Excellent — the model rarely misses fraud."
        : v >= 0.75
        ? "Good — the model catches most fraud."
        : "Many frauds slip through — lower the threshold.",
  },
  {
    key: "f1_score",
    label: "F1-score",
    icon: <FaBalanceScale />,
    accent: "warning",
    hint: "Balance between Precision and Recall",
    describe: (v) =>
      v >= 0.85
        ? "Strong balance between the two."
        : v >= 0.7
        ? "Reasonable balance."
        : "Precision and recall are imbalanced.",
  },
  {
    key: "roc_auc",
    label: "ROC-AUC",
    icon: <FaChartArea />,
    accent: "primary",
    hint: "Overall discrimination ability",
    describe: (v) =>
      v >= 0.97
        ? "Outstanding discrimination."
        : v >= 0.9
        ? "Very good discrimination."
        : "Room for improvement.",
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Performance() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [activeTab, setActiveTab] = useState("metrics"); // 'metrics' | 'charts'

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMetrics();
      setMetrics(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message || "Failed to load metrics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Derived: per-cell percentage of the test set (for the CM grid)
  const cellPercents = useMemo(() => {
    if (!metrics || !metrics.test_set_size) return null;
    const total = metrics.test_set_size;
    return {
      tn: (metrics.true_negatives / total) * 100,
      fp: (metrics.false_positives / total) * 100,
      fn: (metrics.false_negatives / total) * 100,
      tp: (metrics.true_positives / total) * 100,
    };
  }, [metrics]);

  return (
    <div className="perf-page">
      {/* ============================== HEADER ============================== */}
      <header className="perf-header">
        <div className="perf-header-text">
          <div className="perf-header-badge">
            <FaChartArea /> Model Evaluation
          </div>
          <h1>Performance Dashboard</h1>
          <p>
            Evaluation on the held-out test set
            {metrics?.test_set_size
              ? ` · ${metrics.test_set_size.toLocaleString()} transactions`
              : ""}
            {lastUpdated
              ? ` · updated ${lastUpdated.toLocaleTimeString()}`
              : ""}
          </p>
        </div>
        <button
          className="btn btn-secondary perf-refresh-btn"
          onClick={load}
          disabled={loading}
        >
          <FaSyncAlt className={loading ? "spin" : ""} />
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      {/* ============================== ERROR ============================== */}
      {error && (
        <div className="perf-error-card">
          <div className="perf-error-icon">
            <FaExclamationTriangle />
          </div>
          <div className="perf-error-text">
            <h3>Could not load metrics</h3>
            <p>{error}</p>
          </div>
          <button className="btn btn-secondary" onClick={load}>
            Retry
          </button>
        </div>
      )}

      {/* ============================== EMPTY ============================== */}
      {!loading && !metrics && !error && (
        <div className="card">
          <div className="empty-state">
            <FaChartArea size={36} />
            <h3>No metrics available yet</h3>
            <p>
              Run <code>python src/evaluate.py</code> to generate the metrics
              and report images, then reload this page.
            </p>
          </div>
        </div>
      )}

      {/* ============================== METRIC CARDS ============================== */}
      {(loading || metrics) && (
        <section className="perf-metric-grid">
          {loading ? (
            <>
              <div className="skeleton skeleton-stat" />
              <div className="skeleton skeleton-stat" />
              <div className="skeleton skeleton-stat" />
              <div className="skeleton skeleton-stat" />
            </>
          ) : (
            METRIC_CONFIG.map((m) => {
              const value = metrics[m.key];
              return (
                <div key={m.key} className="perf-metric-wrapper">
                  <StatCard
                    label={m.label}
                    value={fmt(value)}
                    icon={m.icon}
                    accent={m.accent}
                    hint={m.hint}
                  />
                  <div className="perf-metric-bar-track">
                    <div
                      className={`perf-metric-bar-fill accent-${m.accent}`}
                      style={{ width: `${Math.min(100, value * 100)}%` }}
                    />
                  </div>
                  <div className="perf-metric-describe">
                    {m.describe(value)}
                  </div>
                </div>
              );
            })
          )}
        </section>
      )}

      {/* ============================== TABS ============================== */}
      {!loading && metrics && (
        <div className="perf-tabs" role="tablist" aria-label="Performance views">
          <button
            role="tab"
            aria-selected={activeTab === "metrics"}
            className={`perf-tab ${activeTab === "metrics" ? "active" : ""}`}
            onClick={() => setActiveTab("metrics")}
            type="button"
          >
            <FaThLarge /> Metrics & Matrix
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "charts"}
            className={`perf-tab ${activeTab === "charts" ? "active" : ""}`}
            onClick={() => setActiveTab("charts")}
            type="button"
          >
            <FaImage /> Report Charts
          </button>
        </div>
      )}

      {/* ============================== TAB: METRICS ============================== */}
      {!loading && metrics && activeTab === "metrics" && (
        <>
          {/* Confusion matrix */}
          <section className="card perf-cm-card">
            <div className="perf-cm-header">
              <h2 className="card-title">Confusion Matrix</h2>
              <span className="perf-cm-total">
                {metrics.test_set_size?.toLocaleString()} total predictions
              </span>
            </div>

            <div className="perf-cm-wrapper">
              {/* Y axis label */}
              <div className="perf-cm-axis-y">Actual</div>

              {/* Grid */}
              <div className="perf-cm-grid">
                {/* Headers */}
                <div />
                <div className="perf-cm-col-header">Predicted Genuine</div>
                <div className="perf-cm-col-header">Predicted Fraud</div>

                {/* Row: Actual Genuine */}
                <div className="perf-cm-row-header">Genuine</div>
                <div className="perf-cm-cell perf-cm-tn">
                  <div className="perf-cm-label">True Negative</div>
                  <div className="perf-cm-value">
                    {metrics.true_negatives.toLocaleString()}
                  </div>
                  <div className="perf-cm-sub">
                    {cellPercents ? `${cellPercents.tn.toFixed(2)}% of test` : ""}
                  </div>
                </div>
                <div className="perf-cm-cell perf-cm-fp">
                  <div className="perf-cm-label">False Positive</div>
                  <div className="perf-cm-value">
                    {metrics.false_positives.toLocaleString()}
                  </div>
                  <div className="perf-cm-sub">
                    {cellPercents ? `${cellPercents.fp.toFixed(2)}% of test` : ""}
                  </div>
                </div>

                {/* Row: Actual Fraud */}
                <div className="perf-cm-row-header">Fraud</div>
                <div className="perf-cm-cell perf-cm-fn">
                  <div className="perf-cm-label">False Negative</div>
                  <div className="perf-cm-value">
                    {metrics.false_negatives.toLocaleString()}
                  </div>
                  <div className="perf-cm-sub">
                    {cellPercents ? `${cellPercents.fn.toFixed(2)}% of test` : ""}
                  </div>
                </div>
                <div className="perf-cm-cell perf-cm-tp">
                  <div className="perf-cm-label">True Positive</div>
                  <div className="perf-cm-value">
                    {metrics.true_positives.toLocaleString()}
                  </div>
                  <div className="perf-cm-sub">
                    {cellPercents ? `${cellPercents.tp.toFixed(2)}% of test` : ""}
                  </div>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="perf-cm-legend">
              <div className="perf-cm-legend-item">
                <span className="perf-cm-legend-swatch perf-cm-tn" />
                <span>
                  <strong>TN</strong> — genuine, correctly kept
                </span>
              </div>
              <div className="perf-cm-legend-item">
                <span className="perf-cm-legend-swatch perf-cm-tp" />
                <span>
                  <strong>TP</strong> — fraud, correctly flagged
                </span>
              </div>
              <div className="perf-cm-legend-item">
                <span className="perf-cm-legend-swatch perf-cm-fp" />
                <span>
                  <strong>FP</strong> — genuine flagged as fraud (annoyance)
                </span>
              </div>
              <div className="perf-cm-legend-item">
                <span className="perf-cm-legend-swatch perf-cm-fn" />
                <span>
                  <strong>FN</strong> — fraud missed (money lost)
                </span>
              </div>
            </div>
          </section>

          {/* Interpretation */}
          <section className="card perf-interpretation">
            <h2 className="card-title">Interpretation</h2>
            <div className="perf-interpretation-grid">
              <div className="perf-interpretation-row">
                <div className="perf-interpretation-icon success">
                  <FaCheckCircle />
                </div>
                <div>
                  <div className="perf-interpretation-title">
                    {metrics.true_positives} of {metrics.actual_frauds} frauds
                    caught
                  </div>
                  <div className="perf-interpretation-sub">
                    Recall ={" "}
                    <strong>{fmt(metrics.recall, 4)}</strong> — the model
                    correctly flagged{" "}
                    {(
                      (metrics.true_positives / metrics.actual_frauds) *
                      100
                    ).toFixed(1)}
                    % of real frauds.
                  </div>
                </div>
              </div>

              <div className="perf-interpretation-row">
                <div className="perf-interpretation-icon warning">
                  <FaExclamationTriangle />
                </div>
                <div>
                  <div className="perf-interpretation-title">
                    {metrics.false_positives} false alarms
                  </div>
                  <div className="perf-interpretation-sub">
                    Only{" "}
                    <strong>
                      {(
                        (metrics.false_positives /
                          (metrics.false_positives + metrics.true_negatives)) *
                        100
                      ).toFixed(4)}
                      %
                    </strong>{" "}
                    of genuine transactions were incorrectly flagged.
                  </div>
                </div>
              </div>

              <div className="perf-interpretation-row">
                <div className="perf-interpretation-icon primary">
                  <FaArrowRight />
                </div>
                <div>
                  <div className="perf-interpretation-title">
                    ROC-AUC of {fmt(metrics.roc_auc, 4)}
                  </div>
                  <div className="perf-interpretation-sub">
                    The model ranks a random fraud above a random genuine
                    transaction{" "}
                    <strong>
                      {(metrics.roc_auc * 100).toFixed(2)}%
                    </strong>{" "}
                    of the time.
                  </div>
                </div>
              </div>
            </div>
          </section>
        </>
      )}

      {/* ============================== TAB: CHARTS ============================== */}
      {!loading && metrics && activeTab === "charts" && (
        <section className="perf-images-grid">
          <ReportImage
            filename="confusion_matrix.png"
            title="Confusion Matrix (Heatmap)"
          />
          <ReportImage filename="roc_curve.png" title="ROC Curve" />
          <ReportImage
            filename="feature_importance.png"
            title="Top 15 Feature Importances"
          />
          <ReportImage
            filename="class_distribution.png"
            title="Class Distribution"
          />
        </section>
      )}

      {/* ============================== FOOTER NOTE ============================== */}
      {!loading && metrics && (
        <footer className="perf-footer-note">
          <FaExpand />
          <span>
            Charts are served from the backend at{" "}
            <code>/api/reports/&lt;filename&gt;</code>. Metrics come from{" "}
            <code>models/metrics.json</code>.
          </span>
        </footer>
      )}
    </div>
  );
}