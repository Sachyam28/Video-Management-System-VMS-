import React, { useState, useEffect } from "react";
import { fetchStreams, fetchResults } from "../api/api";
import "./monitoring.css";

export default function MonitoringCenter() {
  const [streams, setStreams] = useState([]);
  const [results, setResults] = useState({});
  const [logs, setLogs] = useState([]);

  // Load active streams
  useEffect(() => {
    loadStreams();
    const i = setInterval(loadStreams, 4000);
    return () => clearInterval(i);
  }, []);

  const loadStreams = async () => {
    const data = await fetchStreams();
    setStreams(data);
  };

  // DELETE STREAM FUNCTION
  const deleteStream = async (id) => {
    await fetch(`http://localhost:8000/streams/${id}`, {
      method: "DELETE",
    });
    loadStreams();
  };

  // Poll results periodically
  useEffect(() => {
    const interval = setInterval(async () => {
      for (const s of streams) {
        const res = await fetchResults(s.id);
        if (res.length > 0) {
          setResults(prev => ({ ...prev, [s.id]: res[0] }));

          // Add to realtime logs
          setLogs(prev => [
            `[${new Date().toLocaleTimeString()}] Stream ${s.name}: ${JSON.stringify(res[0].result_json)}`,
            ...prev.slice(0, 20)
          ]);
        }
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [streams]);


  return (
    <div className="monitor-container">
      <h1 className="monitor-title">AI Monitoring Center</h1>

      {/* ADD STREAM PANEL */}
      <div className="add-stream-panel">
        <h3>Add Video Stream</h3>

        <input
          placeholder="Stream Name"
          className="neon-input"
          id="streamName"
        />

        <input
          placeholder="Source (video path, RTSP, folder)"
          className="neon-input"
          id="streamSource"
        />

        <button
          onClick={async () => {
            const name = document.getElementById("streamName").value;
            const source = document.getElementById("streamSource").value;

            if (!name || !source) {
              alert("Please enter both name and source");
              return;
            }

            await fetch("http://localhost:8000/streams", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ name, source }),
            });

            document.getElementById("streamName").value = "";
            document.getElementById("streamSource").value = "";

            loadStreams();
          }}
          className="neon-button"
        >
          ➕ Add Stream
        </button>
      </div>


      {/* STREAM CARDS */}
      <div className="monitor-grid">
        {streams.map((s) => {
          const r = results[s.id]?.result_json || {};
          const alert = r.alert === true;

          return (
            <div key={s.id} className={`monitor-card ${alert ? "alert" : ""}`}>
              
              {/* HEADER WITH DELETE BUTTON */}
              <div className="monitor-header">
                <span className="stream-name">{s.name}</span>
                
                <div className="card-actions">
                  <span className={`status-dot ${alert ? "blink-red" : "green"}`}></span>

                  <button
                    className="delete-btn"
                    onClick={() => deleteStream(s.id)}
                  >
                    ✕
                  </button>
                </div>
              </div>

              {/* BODY */}
              <div className="monitor-body">
                <p className="det-title">Latest Detection</p>
                <pre className="det-json">
                  {JSON.stringify(r.detections || [], null, 2)}
                </pre>
              </div>

              {/* ALERT BANNER */}
              {alert && <div className="alert-banner">⚠ ALERT DETECTED</div>}
            
            </div>
          );
        })}
      </div>

      {/* LOG PANEL */}
      <div className="log-panel">
        <h3>Realtime Logs</h3>
        <div className="log-body">
          {logs.map((l, i) => (
            <div key={i} className="log-line">{l}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
