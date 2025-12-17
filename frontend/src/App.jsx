import { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setError("");
    setResult(null);

    if (!file) {
      setError("Please select an XML file first.");
      return;
    }

    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);

      const API_BASE = import.meta.env.VITE_API_BASE_URL;
      const res = await fetch(`${API_BASE}/analyze-dm`, {
        method: "POST",
        body: form
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data?.detail || "Request failed");
      } else {
        setResult(data);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: "0 auto", fontFamily: "system-ui" }}>
      <h2>S1000D 4.1 Data Module Analyzer</h2>
      <p>Upload a Data Module XML file and get a quick structure/quality report.</p>

      <input
        type="file"
        accept=".xml"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <div style={{ marginTop: 12 }}>
        <button onClick={analyze} disabled={loading || !file}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {error && (
        <div style={{ marginTop: 16, color: "crimson" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Result</h3>
          <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 8, overflow: "auto" }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
