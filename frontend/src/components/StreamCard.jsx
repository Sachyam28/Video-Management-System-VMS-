import React, { useEffect, useState } from "react";
import { toggleModel, fetchResults } from "../api/api";

export default function StreamCard({ stream }) {
  const [results, setResults] = useState([]);
  const [hasAlert, setHasAlert] = useState(false);

  useEffect(() => {
    loadResults();

    // Auto-refresh every 3 seconds
    const interval = setInterval(loadResults, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadResults = async () => {
    const data = await fetchResults(stream.id);
    setResults(data);

    // Check alerts
    if (data.some(item => item.alert === true)) {
      setHasAlert(true);
    } else {
      setHasAlert(false);
    }
  };

  return (
    <div style={{
      border: hasAlert ? "2px solid red" : "1px solid #ccc",
      padding: 15,
      borderRadius: 8,
      marginBottom: 15,
      background: hasAlert ? "#ffe5e5" : "#f9f9f9"
    }}>
      <h3>{stream.name}</h3>
      <p><strong>Source:</strong> {stream.source}</p>

      <div style={{ marginTop: 10 }}>
        <strong>Models:</strong>
        <button onClick={() => toggleModel(stream.id, "road_detector", true)}>Enable Road</button>
        <button onClick={() => toggleModel(stream.id, "road_detector", false)}>Disable Road</button>

        <button onClick={() => toggleModel(stream.id, "crack_detector", true)} style={{ marginLeft: 5 }}>
          Enable Crack
        </button>
        <button onClick={() => toggleModel(stream.id, "crack_detector", false)} style={{ marginLeft: 5 }}>
          Disable Crack
        </button>
      </div>

      <div style={{ marginTop: 10 }}>
        <strong>Latest Output:</strong>
        <pre style={{
          background: "#eee",
          padding: 10,
          borderRadius: 5,
          maxHeight: 150,
          overflow: "auto"
        }}>
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>

      {hasAlert && (
        <div style={{
          marginTop: 10,
          padding: 10,
          background: "red",
          color: "white",
          borderRadius: 5
        }}>
          ⚠️ ALERT: Something abnormal detected!
        </div>
      )}
    </div>
  );
}
