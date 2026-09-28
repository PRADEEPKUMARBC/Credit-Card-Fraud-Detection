/**
 * Home.jsx
 * --------
 * Main dashboard for the Credit Card Fraud Detection project.
 *
 * Sections:
 *   1. Hero with tagline, live API status, and quick refresh
 *   2. Four stat cards (Total / Fraud / Genuine / Fraud %)
 *      with animated counters and computed insight hints
 *   3. Fraud-rate callout ("1 in X transactions is fraudulent")
 *   4. Two-column area: model metrics panel + class distribution charts
 *   5. Clickable "Quick Start" cards that link to other pages
 *
 * Every value comes from the FastAPI backend; nothing is hard-coded.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  FaShieldAlt,
  FaCreditCard,
  FaExclamationTriangle,
  FaCheckCircle,
  FaPercentage,
  FaSyncAlt,
  FaArrowRight,
  FaChartBar,
  FaFlask,
  FaBalanceScale,
  FaCheck,
} from "react-icons/fa";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
  Legend,
} from "recharts";

import StatCard from "../components/StatCard";
import MetricBar from "../components/MetricBar";
import { getMetrics, getModelInfo, getStatus } from "../services/api";
import { formatNumber, formatMetric } from "../services/format";

import "../styles/components/StatCard.css";
import "../styles/components/MetricBar.css";
import "../styles/pages/Home.css";

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------
function useCountUp(target, duration = 700) {
  const [display, setDisplay] = useState(target ?? 0);
  const prevRef = useRef(target ?? 0);

  useEffect(() => {
    if (target === null || target === undefined) return;

    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

    if (reduced) {
      setDisplay(target);
      prevRef.current = target;
      return;
    }

    const start = prevRef.current ?? 0;
    const delta = target - start;
    const t0 = performance.now();

    let frame;
    function tick(now) {
      const elapsed = now - t0;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start + delta * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      } else {
        prevRef.current = target;
      }
    }
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return display;
}

function gradeFor(value) {
  if (value >= 0.95) return { label: "Excellent", tone: "success" };
  if (value >= 0.85) return { label: "Very Good", tone: "success" };
  if (value >= 0.75) return { label: "Good", tone: "primary" };
  if (value >= 0.6)  return { label: "Fair", tone: "warning" };
  return { label: "Needs Work", tone: "danger" };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Home() {
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  async function loadAll() {
    setLoading(true);
    setError(null);
    try {
      const [s, m, mi] = await Promise.all([
        getStatus(),
        getMetrics(),
        getModelInfo(),
      ]);
      setStatus(s);
      setMetrics(m);
      setModelInfo(mi);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message || "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  const stats = modelInfo?.dataset_stats || null;

  // ---- Derived values ----
  const total = stats?.total_transactions ?? 0;
  const fraud = stats?.fraud_cases ?? 0;
  const genuine = stats?.genuine_cases ?? 0;
  const fraudPct = stats?.fraud_percentage ?? 0;

  const oneInX = useMemo(() => {
    if (!fraud || !total) return null;
    return Math.round(total / fraud);
  }, [fraud, total]);

  const animatedTotal = useCountUp(total);
  const animatedFraud = useCountUp(fraud);
  const animatedGenuine = useCountUp(genuine);

  // ---- Chart data ----
  const chartData = useMemo(
    () => [
      { name: "Genuine", count: genuine, fill: "#2e86ab" },
      { name: "Fraud", count: fraud, fill: "#dc2626" },
    ],
    [genuine, fraud]
  );

  const chartHasData = genuine + fraud > 0;

  return (
    <div className="home-page">
      {/* ============================== HERO ============================== */}
      <section className="home-hero">
        <div className="home-hero-main">
          <div className="home-hero-icon">
            <FaShieldAlt size={38} />
          </div>
          <div className="home-hero-text">
            <div className="home-hero-badge">Live Fraud Detection Console</div>
            <h1>Credit Card Fraud Detection</h1>
            <p className="home-subtitle">
              Binary classification using a{" "}
              <strong>Random Forest</strong> trained on{" "}
              <strong>SMOTE-balanced data</strong>, served via{" "}
              <strong>FastAPI</strong> and visualized in{" "}
              <strong>React</strong>.
            </p>
          </div>
        </div>

        <div className="home-hero-side">
          <div className="home-hero-status">
            <span
              className={`badge ${
                status
                  ? "badge-success"
                  : loading
                  ? "badge-warning"
                  : "badge-danger"
              }`}
            >
              <span
                className={`home-status-dot ${
                  status ? "online" : loading ? "checking" : "offline"
                }`}
                aria-hidden="true"
              />
              {status ? "API Online" : loading ? "Connecting…" : "API Offline"}
            </span>
            {lastUpdated && (
              <span className="home-last-updated">
                Updated {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
          <button
            className="btn btn-primary home-refresh-btn"
            onClick={loadAll}
            disabled={loading}
          >
            <FaSyncAlt className={loading ? "spin" : ""} />
            {loading ? "Refreshing…" : "Refresh Data"}
          </button>
        </div>
      </section>

      {/* ============================== ERROR ============================== */}
      {error && (
        <div className="home-error-card">
          <div className="home-error-icon">
            <FaExclamationTriangle />
          </div>
          <div className="home-error-text">
            <h3>Could not load dashboard</h3>
            <p>{error}</p>
          </div>
          <button className="btn btn-secondary" onClick={loadAll}>
            Retry
          </button>
        </div>
      )}

      {/* ============================== STAT CARDS ============================== */}
      <section className="home-stats-grid">
        {loading ? (
          <>
            <div className="skeleton skeleton-stat" />
            <div className="skeleton skeleton-stat" />
            <div className="skeleton skeleton-stat" />
            <div className="skeleton skeleton-stat" />
          </>
        ) : (
          <>
            <StatCard
              label="Total Transactions"
              value={formatNumber(animatedTotal)}
              icon={<FaCreditCard />}
              accent="primary"
              hint="After duplicate removal"
            />
            <StatCard
              label="Fraud Cases"
              value={formatNumber(animatedFraud)}
              icon={<FaExclamationTriangle />}
              accent="danger"
              hint="Class 1 — the minority"
            />
            <StatCard
              label="Genuine Cases"
              value={formatNumber(animatedGenuine)}
              icon={<FaCheckCircle />}
              accent="success"
              hint="Class 0 — the majority"
            />
            <StatCard
              label="Fraud Percentage"
              value={
                stats ? `${Number(fraudPct).toFixed(4)}%` : "—"
              }
              icon={<FaPercentage />}
              accent="warning"
              hint={
                oneInX ? `About 1 in ${oneInX.toLocaleString()}` : "Share of fraud"
              }
            />
          </>
        )}
      </section>

      {/* ============================== FRAUD-RATE CALLOUT ============================== */}
      {!loading && stats && oneInX && (
        <section className="home-callout">
          <div className="home-callout-icon">
            <FaExclamationTriangle />
          </div>
          <div className="home-callout-text">
            <div className="home-callout-title">
              About 1 in {oneInX.toLocaleString()} transactions is fraudulent
            </div>
            <div className="home-callout-sub">
              This severe class imbalance is why we use <strong>SMOTE</strong>{" "}
              on the training data and report <strong>Precision</strong>,{" "}
              <strong>Recall</strong>, <strong>F1</strong>, and{" "}
              <strong>ROC-AUC</strong> instead of accuracy.
            </div>
          </div>
          <Link to="/about" className="home-callout-cta">
            Learn why <FaArrowRight />
          </Link>
        </section>
      )}

      {/* ============================== TWO-COLUMN ============================== */}
      <section className="home-two-col">
        {/* Model Performance */}
        <div className="card home-metrics-card">
          <div className="home-card-header">
            <h2 className="card-title">Model Performance</h2>
            <span className="home-card-tag">Test set</span>
          </div>

          {loading && <div className="skeleton skeleton-chart" />}

          {!loading && metrics && (
            <div className="home-metrics">
              <MetricRow
                label="Precision"
                value={metrics.precision}
                color="#2e86ab"
              />
              <MetricRow
                label="Recall"
                value={metrics.recall}
                color="#16a34a"
              />
              <MetricRow
                label="F1-score"
                value={metrics.f1_score}
                color="#d97706"
              />
              <MetricRow
                label="ROC-AUC"
                value={metrics.roc_auc}
                color="#1e3a8a"
              />

              <div className="home-metrics-detail">
                <ConfusionPill
                  label="True Positives"
                  short="TP"
                  value={metrics.true_positives}
                  tone="primary"
                />
                <ConfusionPill
                  label="False Positives"
                  short="FP"
                  value={metrics.false_positives}
                  tone="warning"
                />
                <ConfusionPill
                  label="False Negatives"
                  short="FN"
                  value={metrics.false_negatives}
                  tone="danger"
                />
                <ConfusionPill
                  label="True Negatives"
                  short="TN"
                  value={metrics.true_negatives}
                  tone="success"
                />
              </div>
            </div>
          )}

          {!loading && !metrics && (
            <div className="empty-state">
              <FaChartBar size={28} />
              <h3>No metrics yet</h3>
              <p>Run <code>python src/evaluate.py</code> to generate them.</p>
            </div>
          )}
        </div>

        {/* Class Distribution */}
        <div className="card home-chart-card">
          <div className="home-card-header">
            <h2 className="card-title">Class Distribution</h2>
            <span className="home-card-tag">Full dataset</span>
          </div>

          {loading && <div className="skeleton skeleton-chart" />}

          {!loading && chartHasData && (
            <>
              <div className="home-chart-wrap">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart
                    data={chartData}
                    margin={{ top: 10, right: 16, left: 0, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" />
                    <YAxis
                      tickFormatter={(v) =>
                        v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v
                      }
                    />
                    <Tooltip
                      formatter={(value) => Number(value).toLocaleString()}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                      {chartData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="home-chart-note">
                <FaCheck className="home-chart-note-check" />
                Fraud is barely visible on a linear scale — see the{" "}
                <Link to="/performance">Performance page</Link> for the
                log-scale view.
              </div>
            </>
          )}

          {!loading && !chartHasData && (
            <div className="empty-state">
              <FaChartBar size={28} />
              <h3>No chart data</h3>
              <p>Dataset statistics were not available from the backend.</p>
            </div>
          )}
        </div>
      </section>

      {/* ============================== QUICK START ============================== */}
      <section className="home-quickstart-section">
        <div className="home-card-header">
          <h2 className="card-title">Quick Start</h2>
          <span className="home-card-tag">3 steps</span>
        </div>

        <div className="home-quickstart-grid">
          <Link to="/predict" className="home-quickstart-card">
            <div className="home-quickstart-icon accent-primary">
              <FaFlask />
            </div>
            <div className="home-quickstart-body">
              <div className="home-quickstart-title">
                Try a prediction
              </div>
              <div className="home-quickstart-text">
                Load a real fraud or genuine example, then run the model to see
                the probability and risk level.
              </div>
            </div>
            <FaArrowRight className="home-quickstart-arrow" />
          </Link>

          <Link to="/performance" className="home-quickstart-card">
            <div className="home-quickstart-icon accent-success">
              <FaBalanceScale />
            </div>
            <div className="home-quickstart-body">
              <div className="home-quickstart-title">
                Inspect performance
              </div>
              <div className="home-quickstart-text">
                Confusion matrix, ROC curve, feature importances, and per-metric
                interpretation.
              </div>
            </div>
            <FaArrowRight className="home-quickstart-arrow" />
          </Link>

          <Link to="/about" className="home-quickstart-card">
            <div className="home-quickstart-icon accent-warning">
              <FaShieldAlt />
            </div>
            <div className="home-quickstart-body">
              <div className="home-quickstart-title">
                Understand the project
              </div>
              <div className="home-quickstart-text">
                Dataset, pipeline, SMOTE, why we report the metrics we report,
                and the tech stack.
              </div>
            </div>
            <FaArrowRight className="home-quickstart-arrow" />
          </Link>
        </div>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Small sub-components
// ---------------------------------------------------------------------------
function MetricRow({ label, value, color }) {
  const grade = gradeFor(value);
  return (
    <div className="home-metric-row">
      <div className="home-metric-row-top">
        <span className="home-metric-row-label">{label}</span>
        <span className={`home-grade home-grade-${grade.tone}`}>
          {grade.label}
        </span>
      </div>
      <MetricBar label="" value={value} color={color} />
      <div className="home-metric-row-value">{formatMetric(value)}</div>
    </div>
  );
}

function ConfusionPill({ label, short, value, tone }) {
  return (
    <div className={`home-confusion-pill home-confusion-${tone}`}>
      <div className="home-confusion-short">{short}</div>
      <div className="home-confusion-value">
        {Number(value).toLocaleString()}
      </div>
      <div className="home-confusion-label">{label}</div>
    </div>
  );
}