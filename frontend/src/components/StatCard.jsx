/**
 * StatCard.jsx
 * ------------
 * A compact card showing a big number, a label, an icon, and a color accent.
 */

export default function StatCard({
  label,
  value,
  icon,
  accent = "primary",
  hint,
}) {
  return (
    <div className={`stat-card stat-card-${accent}`}>
      <div className="stat-card-icon">{icon}</div>
      <div className="stat-card-body">
        <div className="stat-card-label">{label}</div>
        <div className="stat-card-value">{value}</div>
        {hint && <div className="stat-card-hint">{hint}</div>}
      </div>
    </div>
  );
}