/**
 * ResultCard.jsx
 * --------------
 * Renders the prediction result returned by /predict.
 * Shows:
 *   - a big status icon (genuine vs fraudulent)
 *   - a headline label
 *   - a probability bar
 *   - a risk-level badge
 */

import {
  FaCheckCircle,
  FaExclamationTriangle,
  FaShieldAlt,
} from "react-icons/fa";

const COLORS = {
  Low:    { badge: "badge-success", bar: "#16a34a", bg: "#dcfce7" },
  Medium: { badge: "badge-warning", bar: "#d97706", bg: "#fef3c7" },
  High:   { badge: "badge-danger",  bar: "#dc2626", bg: "#fee2e2" },
};

export default function ResultCard({ result }) {
  if (!result) return null;

  const isFraud = result.class === 1;
  const risk = result.risk_level || "Low";
  const palette = COLORS[risk] || COLORS.Low;
  const pct = Math.round((result.fraud_probability || 0) * 100);

  return (
    <div className="card result-card">
      <div
        className="result-card-header"
        style={{ background: palette.bg, color: palette.bar }}
      >
        {isFraud ? (
          <FaExclamationTriangle size={36} />
        ) : (
          <FaCheckCircle size={36} />
        )}
        <div>
          <div className="result-card-headline">
            {isFraud ? "Fraudulent Transaction" : "Genuine Transaction"}
          </div>
          <div className="result-card-sub">
            The model classified this transaction as class{" "}
            <strong>{result.class}</strong>.
          </div>
        </div>
      </div>

      <div className="result-card-body">
        <div className="result-card-prob">
          <div className="result-card-prob-label">
            <FaShieldAlt /> Fraud Probability
          </div>
          <div className="result-card-prob-value">{pct}%</div>
          <div className="result-card-prob-bar">
            <div
              className="result-card-prob-fill"
              style={{ width: `${pct}%`, background: palette.bar }}
            />
          </div>
        </div>

        <div className="result-card-meta">
          <div>
            <span className="result-card-meta-label">Risk Level</span>
            <span className={`badge ${palette.badge}`}>{risk}</span>
          </div>
          <div>
            <span className="result-card-meta-label">Threshold</span>
            <span className="result-card-meta-value">{result.threshold_used}</span>
          </div>
          <div>
            <span className="result-card-meta-label">Prediction</span>
            <span className="result-card-meta-value">{result.prediction}</span>
          </div>
        </div>

        <div className="result-card-explain">
          {isFraud ? (
            <p>
              The model's fraud probability for this transaction is{" "}
              <strong>{pct}%</strong>, above the 50% decision threshold. The
              transaction should be flagged for manual review.
            </p>
          ) : (
            <p>
              The model's fraud probability for this transaction is{" "}
              <strong>{pct}%</strong>, below the 50% decision threshold. The
              transaction appears legitimate.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}