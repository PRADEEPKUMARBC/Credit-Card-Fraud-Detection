/**
 * Layout.jsx
 * ----------
 * Page shell: header with navigation, main content area, footer.
 * Wraps the routed content in a fade-slide transition on route change.
 */

import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  FaShieldAlt,
  FaHome,
  FaSearchDollar,
  FaChartBar,
  FaInfoCircle,
} from "react-icons/fa";
import { useEffect, useState } from "react";
import { getHealth } from "../services/api";
import "../styles/components/Layout.css";

const NAV_ITEMS = [
  { to: "/",            label: "Dashboard",   icon: <FaHome /> },
  { to: "/predict",     label: "Predict",     icon: <FaSearchDollar /> },
  { to: "/performance", label: "Performance", icon: <FaChartBar /> },
  { to: "/about",       label: "About",       icon: <FaInfoCircle /> },
];

export default function Layout() {
  const location = useLocation();
  const [apiOnline, setApiOnline] = useState(null);

  // Poll the health endpoint every 20 seconds
  useEffect(() => {
    let cancelled = false;

    async function ping() {
      try {
        await getHealth();
        if (!cancelled) setApiOnline(true);
      } catch {
        if (!cancelled) setApiOnline(false);
      }
    }

    ping();
    const interval = setInterval(ping, 20000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const statusDotClass =
    apiOnline === null
      ? "layout-status-dot layout-status-dot-checking"
      : apiOnline
      ? "layout-status-dot layout-status-dot-online"
      : "layout-status-dot layout-status-dot-offline";

  const statusLabel =
    apiOnline === null
      ? "Checking API…"
      : apiOnline
      ? "API Online"
      : "API Offline";

  return (
    <div className="layout">
      <header className="layout-header">
        <div className="container layout-header-inner">
          <div className="layout-brand">
            <FaShieldAlt size={22} />
            <span>FraudGuard</span>
          </div>
          <nav className="layout-nav" aria-label="Primary">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  "layout-nav-link" + (isActive ? " active" : "")
                }
              >
                {item.icon}
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="layout-status" title={statusLabel}>
            <span className={statusDotClass} aria-hidden="true" />
            <span className="layout-status-text">{statusLabel}</span>
          </div>
        </div>
      </header>

      <main className="layout-main">
        <div className="container">
          {/* key forces remount so the page-in animation replays */}
          <div key={location.pathname} className="page-transition">
            <Outlet />
          </div>
        </div>
      </main>

      <footer className="layout-footer">
        <div className="container">
          <span>
            Credit Card Fraud Detection · Machine Learning Project ·{" "}
            {new Date().getFullYear()}
          </span>
        </div>
      </footer>
    </div>
  );
}