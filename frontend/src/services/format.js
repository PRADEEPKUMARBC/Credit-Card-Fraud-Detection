/**
 * format.js
 * ---------
 * Small formatting helpers used across pages so we don't repeat logic.
 */

/** Format an integer with thousands separators. */
export function formatNumber(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString();
}

/** Format a decimal probability/metric with a fixed number of decimals. */
export function formatMetric(value, digits = 4) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

/** Format a 0..1 value as a percentage. */
export function formatPercent(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

/** Format an ISO-like timestamp for the header/footer if needed. */
export function formatDate(d = new Date()) {
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}