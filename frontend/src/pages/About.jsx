/**
 * About.jsx
 * ---------
 * Polished about page for the Credit Card Fraud Detection project.
 *
 * Presents the project as a product page:
 *   - Hero with tagline and quick stats
 *   - Icon-accented section cards
 *   - Dataset stat grid
 *   - Vertical pipeline timeline
 *   - "Why these metrics" side-by-side comparison
 *   - Tech-stack card grid
 *   - Call-to-action footer
 */

import {
  FaGithub,
  FaDatabase,
  FaCogs,
  FaChartLine,
  FaShieldAlt,
  FaPython,
  FaServer,
  FaReact,
  FaCheckCircle,
  FaExclamationTriangle,
  FaArrowUp,
  FaBrain,
  FaBalanceScale,
  FaEye,
} from "react-icons/fa";
import "../styles/pages/About.css";

// ---------------------------------------------------------------------------
// Content data — kept outside JSX so the markup stays readable
// ---------------------------------------------------------------------------
const QUICK_STATS = [
  { label: "Transactions", value: "284,807" },
  { label: "Fraud Cases",  value: "492" },
  { label: "Fraud Rate",   value: "0.17%" },
  { label: "Features",     value: "30" },
];

const DATASET_STATS = [
  { label: "Total rows",   value: "284,807" },
  { label: "Genuine (0)",  value: "284,315" },
  { label: "Fraudulent (1)", value: "492" },
  { label: "Time span",    value: "2 days" },
  { label: "Source",       value: "Kaggle · ULB" },
  { label: "Target column", value: "Class" },
];

const PIPELINE_STEPS = [
  { title: "Load",              text: "Read creditcard.csv into a DataFrame" },
  { title: "Clean",             text: "Drop exact duplicate rows" },
  { title: "Separate",          text: "Features (X) vs target (y = Class)" },
  { title: "Split",             text: "Stratified 80/20 train-test split" },
  { title: "Scale",             text: "Fit StandardScaler on training data only" },
  { title: "Balance",           text: "SMOTE on the training set only" },
  { title: "Train",             text: "Random Forest Classifier (100 trees)" },
  { title: "Evaluate",          text: "Precision, Recall, F1, ROC-AUC on the test set" },
  { title: "Persist",           text: "Save model + scaler with Joblib" },
  { title: "Serve",             text: "Expose predictions through FastAPI" },
  { title: "Visualize",         text: "Consume the API from a React dashboard" },
];

const TECH_STACK = [
  {
    title: "Machine Learning",
    icon: <FaBrain />,
    accent: "primary",
    items: [
      "Python · NumPy · Pandas",
      "scikit-learn — Random Forest",
      "imbalanced-learn — SMOTE",
      "Matplotlib · Seaborn",
      "Joblib — model persistence",
    ],
  },
  {
    title: "Backend",
    icon: <FaServer />,
    accent: "success",
    items: [
      "FastAPI — REST framework",
      "Uvicorn — ASGI server",
      "Pydantic — validation",
      "Joblib — model loading",
    ],
  },
  {
    title: "Frontend",
    icon: <FaReact />,
    accent: "warning",
    items: [
      "React 18 + Vite",
      "React Router — routing",
      "Axios — HTTP client",
      "Recharts — charts",
      "React Icons — iconography",
    ],
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function About() {
  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <div className="about-page">
      {/* ---------------------------- HERO ---------------------------- */}
      <section className="about-hero">
        <div className="about-hero-badge">
          <FaShieldAlt /> Machine Learning Project
        </div>
        <h1>Detecting Fraud at 0.17% Signal Strength</h1>
        <p className="about-hero-tagline">
          An end-to-end system that predicts whether a credit card transaction
          is <strong>Genuine (0)</strong> or <strong>Fraudulent (1)</strong>{" "}
          using a Random Forest Classifier trained on SMOTE-balanced data,
          served through FastAPI and consumed by a React dashboard.
        </p>

        <div className="about-hero-stats">
          {QUICK_STATS.map((s) => (
            <div key={s.label} className="about-hero-stat">
              <div className="about-hero-stat-value">{s.value}</div>
              <div className="about-hero-stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ---------------------------- GOAL ---------------------------- */}
      <section className="about-section">
        <div className="about-section-header">
          <span className="about-section-icon accent-primary">
            <FaShieldAlt />
          </span>
          <h2>Goal</h2>
        </div>
        <p className="about-section-body">
          Given a single credit card transaction described by 30 numeric
          features, predict whether it is <strong>Genuine (0)</strong> or{" "}
          <strong>Fraudulent (1)</strong>. The system must handle the severe
          class imbalance in the dataset (fraud is less than 0.2% of rows) and
          return a calibrated fraud probability along with a risk level.
        </p>
      </section>

      {/* ---------------------------- DATASET ---------------------------- */}
      <section className="about-section">
        <div className="about-section-header">
          <span className="about-section-icon accent-info">
            <FaDatabase />
          </span>
          <h2>Dataset</h2>
        </div>

        <div className="about-dataset-grid">
          <div className="about-dataset-text">
            <p>
              The publicly available <em>Credit Card Fraud Detection</em>{" "}
              dataset from Kaggle (ULB Machine Learning Group). It contains{" "}
              <strong>284,807</strong> transactions collected over two days,
              of which <strong>492</strong> are fraudulent.
            </p>
            <p>
              Features <code>V1</code>–<code>V28</code> are the result of a PCA
              transformation applied by the dataset authors to protect
              cardholder privacy. Only <code>Time</code> and{" "}
              <code>Amount</code> remain in their original scales and are
              standardized during preprocessing.
            </p>
          </div>

          <div className="about-dataset-stats">
            {DATASET_STATS.map((s) => (
              <div key={s.label} className="about-dataset-stat">
                <div className="about-dataset-stat-label">{s.label}</div>
                <div className="about-dataset-stat-value">{s.value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------- PIPELINE ---------------------------- */}
      <section className="about-section">
        <div className="about-section-header">
          <span className="about-section-icon accent-warning">
            <FaCogs />
          </span>
          <h2>Pipeline</h2>
        </div>
        <p className="about-section-body about-section-intro">
          From raw CSV to a live web application in eleven steps. Everything
          that <em>learns</em> from data — the scaler and SMOTE — is fit on the
          training set only, to prevent data leakage.
        </p>

        <ol className="about-timeline">
          {PIPELINE_STEPS.map((step, i) => (
            <li key={step.title} className="about-timeline-item">
              <span className="about-timeline-node">{i + 1}</span>
              <div className="about-timeline-content">
                <div className="about-timeline-title">{step.title}</div>
                <div className="about-timeline-text">{step.text}</div>
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------------------------- METRICS ---------------------------- */}
      <section className="about-section">
        <div className="about-section-header">
          <span className="about-section-icon accent-danger">
            <FaChartLine />
          </span>
          <h2>Why These Metrics?</h2>
        </div>
        <p className="about-section-body about-section-intro">
          Accuracy is misleading on imbalanced data. On this dataset, a model
          that predicts <em>"genuine"</em> for every transaction scores{" "}
          <strong>99.83% accuracy</strong> while catching <strong>zero</strong>{" "}
          fraud. We therefore rely on the metrics below.
        </p>

        <div className="about-metrics-grid">
          <div className="about-metric-card">
            <div className="about-metric-icon danger">
              <FaExclamationTriangle />
            </div>
            <h3>Accuracy — the trap</h3>
            <p>
              A "guess genuine every time" model would score{" "}
              <strong>99.83%</strong> accuracy. It is worthless. Accuracy
              hides failure on rare classes.
            </p>
          </div>

          <div className="about-metric-icon-card">
            <div className="about-metric-icon success">
              <FaBalanceScale />
            </div>
            <h3>Precision & Recall</h3>
            <p>
              <strong>Precision</strong> asks: of all transactions flagged as
              fraud, how many truly were fraud? <strong>Recall</strong> asks:
              of all real frauds, how many did we catch? Fraud detection
              usually prioritizes recall.
            </p>
          </div>

          <div className="about-metric-card">
            <div className="about-metric-icon primary">
              <FaEye />
            </div>
            <h3>F1 & ROC-AUC</h3>
            <p>
              <strong>F1</strong> balances precision and recall into a single
              number. <strong>ROC-AUC</strong> measures how well the model
              ranks fraud above genuine across every possible threshold —
              perfect for imbalanced detection.
            </p>
          </div>
        </div>
      </section>

      {/* ---------------------------- TECH STACK ---------------------------- */}
      <section className="about-section">
        <div className="about-section-header">
          <span className="about-section-icon accent-primary">
            <FaPython />
          </span>
          <h2>Tech Stack</h2>
        </div>

        <div className="about-stack-grid">
          {TECH_STACK.map((stack) => (
            <div
              key={stack.title}
              className={`about-stack-card accent-${stack.accent}`}
            >
              <div className="about-stack-icon">{stack.icon}</div>
              <h3>{stack.title}</h3>
              <ul>
                {stack.items.map((item) => (
                  <li key={item}>
                    <FaCheckCircle className="about-stack-check" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* ---------------------------- CTA ---------------------------- */}
      <section className="about-cta">
        <div className="about-cta-text">
          <h2>Explore the project</h2>
          <p>
            Source code, documentation, tests, and setup instructions are
            available on GitHub.
          </p>
        </div>
        <div className="about-cta-actions">
          <a
            className="btn btn-primary"
            href="https://github.com/your-username/credit-card-fraud-detection"
            target="_blank"
            rel="noreferrer noopener"
          >
            <FaGithub /> View on GitHub
          </a>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={scrollToTop}
            aria-label="Scroll back to top"
          >
            <FaArrowUp /> Back to top
          </button>
        </div>
      </section>
    </div>
  );
}