/**
 * api.js
 * ------
 * Central wrapper around every backend call.
 *
 * All requests go through the Vite proxy path `/api/...`, which Vite
 * forwards to the FastAPI backend at http://127.0.0.1:8000 (dev only).
 * In production you would set up an equivalent reverse proxy.
 *
 * Every function returns the parsed response body (or throws).
 * Components should catch errors and show a user-friendly message.
 */

import axios from "axios";

// Base URL for every request.
// In dev, Vite proxies "/api/*" to the FastAPI server (see vite.config.js).
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

// Axios instance with sensible defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

// Normalize errors so components get a plain message
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = "Unknown error";
    if (error.response) {
      const detail = error.response.data?.detail ?? error.response.data?.error;
      message =
        typeof detail === "string"
          ? detail
          : `Request failed with status ${error.response.status}`;
    } else if (error.request) {
      message = "No response from server. Is the backend running?";
    } else {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/** GET /  — API status */
export async function getStatus() {
  const { data } = await api.get("/");
  return data;
}

/** GET /health — liveness probe */
export async function getHealth() {
  const { data } = await api.get("/health");
  return data;
}

/** POST /predict — single transaction prediction */
export async function predictTransaction(transaction) {
  const { data } = await api.post("/predict", transaction);
  return data;
}

/** POST /predict/batch — many transactions at once */
export async function predictBatch(transactions) {
  const { data } = await api.post("/predict/batch", { transactions });
  return data;
}

/** GET /metrics — model evaluation metrics */
export async function getMetrics() {
  const { data } = await api.get("/metrics");
  return data;
}

/** GET /model-info — metadata + plain-text summary */
export async function getModelInfo() {
  const { data } = await api.get("/model-info");
  return data;
}

/** GET /reports — list of available PNG filenames */
export async function getReports() {
  const { data } = await api.get("/reports");
  return data.reports || [];
}

/**
 * Build a full URL to a report image.
 * Example: getReportImageUrl("confusion_matrix.png")
 *   -> "/api/reports/confusion_matrix.png"
 */
export function getReportImageUrl(filename) {
  return `${API_BASE_URL}/reports/${filename}`;
}

export default api;