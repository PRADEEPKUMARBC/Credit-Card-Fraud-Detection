/**
 * ReportImage.jsx
 * ---------------
 * Loads a PNG from the backend /reports endpoint and displays it inside a card.
 * Shows a loading placeholder and a friendly error if the image is missing.
 */

import { useEffect, useState } from "react";
import { FaImage } from "react-icons/fa";
import { getReportImageUrl } from "../services/api";

export default function ReportImage({ filename, title }) {
  const [state, setState] = useState("loading"); // 'loading' | 'loaded' | 'error'
  const url = getReportImageUrl(filename);

  useEffect(() => {
    setState("loading");
  }, [filename]);

  return (
    <div className="card report-image-card">
      <h3 className="card-title">{title || filename}</h3>
      {state === "loading" && (
        <div className="report-image-placeholder">
          <FaImage size={28} />
          <span>Loading image…</span>
        </div>
      )}
      {state === "error" && (
        <div className="report-image-placeholder report-image-error">
          <FaImage size={28} />
          <span>Image not available</span>
          <code>{filename}</code>
        </div>
      )}
      <img
        src={url}
        alt={title || filename}
        className="report-image"
        style={{ display: state === "loaded" ? "block" : "none" }}
        onLoad={() => setState("loaded")}
        onError={() => setState("error")}
      />
    </div>
  );
}