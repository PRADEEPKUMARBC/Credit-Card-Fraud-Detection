/**
 * MetricBar.jsx
 * -------------
 * Displays a 0–1 metric as a horizontal progress bar with its numeric value.
 * Used on both Home and Performance pages.
 */

export default function MetricBar({ label, value, color = "#2e86ab" }) {
  const pct = Math.max(0, Math.min(100, (value || 0) * 100));

  return (
    <div className="metric-bar">
      <div className="metric-bar-top">
        <span className="metric-bar-label">{label}</span>
        <span className="metric-bar-value">{(value || 0).toFixed(4)}</span>
      </div>
      <div className="metric-bar-track">
        <div
          className="metric-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}