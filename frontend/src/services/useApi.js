/**
 * useApi.js
 * ---------
 * Small custom hook that standardizes async request handling:
 *   - tracks data / error / loading
 *   - exposes a `run(...)` function you can call any time
 *
 * Usage:
 *   const { data, error, loading, run } = useApi(predictTransaction);
 *   ...
 *   onClick={() => run(transaction)}
 */

import { useCallback, useState } from "react";

export default function useApi(asyncFn) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await asyncFn(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || "Request failed");
        setData(null);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [asyncFn]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, error, loading, run, reset };
}