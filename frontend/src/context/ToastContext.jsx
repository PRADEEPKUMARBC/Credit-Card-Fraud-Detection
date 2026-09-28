/**
 * ToastContext.jsx
 * ----------------
 * Tiny toast notification system.
 *
 * Usage:
 *   const toast = useToast();
 *   toast.success("Saved!");
 *   toast.error("Something went wrong.");
 *   toast.info("Heads up.");
 *
 * Toasts auto-dismiss after a few seconds. Toasts stack vertically at the
 * top-right corner of the viewport.
 */

import { createContext, useCallback, useContext, useState } from "react";
import {
  FaCheckCircle,
  FaExclamationCircle,
  FaInfoCircle,
  FaTimes,
} from "react-icons/fa";
import "../styles/components/Toast.css";

const ToastContext = createContext(null);

let nextId = 1;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (type, message, duration = 3500) => {
      const id = nextId++;
      setToasts((prev) => [...prev, { id, type, message }]);
      if (duration > 0) {
        setTimeout(() => remove(id), duration);
      }
      return id;
    },
    [remove]
  );

  const api = {
    success: (msg, duration) => push("success", msg, duration),
    error:   (msg, duration) => push("error",   msg, duration),
    info:    (msg, duration) => push("info",    msg, duration),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-container" aria-live="polite" aria-atomic="false">
        {toasts.map((t) => (
          <Toast key={t.id} toast={t} onClose={() => remove(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function Toast({ toast, onClose }) {
  const icon = {
    success: <FaCheckCircle />,
    error:   <FaExclamationCircle />,
    info:    <FaInfoCircle />,
  }[toast.type];

  return (
    <div className={`toast toast-${toast.type}`} role="status">
      <span className="toast-icon">{icon}</span>
      <span className="toast-message">{toast.message}</span>
      <button
        className="toast-close"
        aria-label="Dismiss"
        onClick={onClose}
        type="button"
      >
        <FaTimes />
      </button>
    </div>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used inside a <ToastProvider>.");
  }
  return ctx;
}