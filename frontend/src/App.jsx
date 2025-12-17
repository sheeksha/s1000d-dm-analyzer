import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeDM = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(
      "https://YOUR-RENDER-URL.onrender.com/analyze-dm",
      {
        method: "POST",
        body: formData
      }
    );

    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>S1000D 4.1 Data Module Analyzer</h2>

      <input type="file" accept=".xml" onChange={e => setFile(e.target.files[0])} />

      <br /><br />

      <button onClick={analyzeDM} disabled={!file || loading}>
        {loading ? "Analyzing..." : "Analyze DM"}
      </button>

      {result && (
        <pre style={{ marginTop: "2rem" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default App;
