/**
 * PredictionForm.jsx
 * ------------------
 * A form with one input per model feature (Time, V1..V28, Amount).
 * Includes buttons to load a real fraud or genuine example row.
 * Calls onPredict(transactionDict) when the user submits.
 */

import { useState } from "react";
import { FaPlay, FaFlask, FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";
import { FEATURE_NAMES, FRAUD_EXAMPLE, GENUINE_EXAMPLE } from "../services/examples";

// Empty form: all zeros
const emptyForm = Object.fromEntries(FEATURE_NAMES.map((f) => [f, "0"]));

export default function PredictionForm({ onPredict, loading }) {
  const [values, setValues] = useState(emptyForm);
  const [errors, setErrors] = useState({});

  function handleChange(name, raw) {
    setValues((prev) => ({ ...prev, [name]: raw }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  function loadExample(example, label) {
    const asStrings = Object.fromEntries(
      Object.entries(example).map(([k, v]) => [k, String(v)])
    );
    setValues(asStrings);
    setErrors({});
    console.info(`[PredictionForm] Loaded ${label} example.`);
  }

  function validate() {
    const newErrors = {};
    for (const name of FEATURE_NAMES) {
      const raw = values[name];
      if (raw === "" || raw === null || raw === undefined) {
        newErrors[name] = "Required";
        continue;
      }
      const num = Number(raw);
      if (Number.isNaN(num)) {
        newErrors[name] = "Must be a number";
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;

    // Convert every value to a number before sending
    const transaction = Object.fromEntries(
      FEATURE_NAMES.map((name) => [name, Number(values[name])])
    );
    onPredict(transaction);
  }

  return (
    <form className="card predict-form" onSubmit={handleSubmit}>
      <div className="predict-form-toolbar">
        <h2 className="card-title" style={{ margin: 0 }}>
          Transaction Features
        </h2>
        <div className="predict-form-toolbar-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => loadExample(FRAUD_EXAMPLE, "fraud")}
          >
            <FaExclamationTriangle color="#dc2626" /> Load Fraud Example
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => loadExample(GENUINE_EXAMPLE, "genuine")}
          >
            <FaCheckCircle color="#16a34a" /> Load Genuine Example
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setValues(emptyForm);
              setErrors({});
            }}
          >
            <FaFlask /> Reset
          </button>
        </div>
      </div>

      <div className="form-grid">
        {FEATURE_NAMES.map((name) => (
          <div className="form-field" key={name}>
            <label htmlFor={`field-${name}`}>{name}</label>
            <input
              id={`field-${name}`}
              type="text"
              inputMode="decimal"
              value={values[name]}
              onChange={(e) => handleChange(name, e.target.value)}
              className={errors[name] ? "error" : ""}
            />
            {errors[name] && (
              <span className="field-error">{errors[name]}</span>
            )}
          </div>
        ))}
      </div>

      <div className="predict-form-footer">
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          <FaPlay /> {loading ? "Predicting…" : "Predict Transaction"}
        </button>
      </div>
    </form>
  );
}