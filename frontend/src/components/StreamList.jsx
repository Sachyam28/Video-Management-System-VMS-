import React, { useEffect, useState } from "react";
import { fetchStreams, createStream } from "../api/api";
import StreamCard from "./StreamCard";

export default function StreamList() {
  const [streams, setStreams] = useState([]);
  const [name, setName] = useState("");
  const [source, setSource] = useState("");

  useEffect(() => {
    loadStreams();
  }, []);

  const loadStreams = async () => {
    const data = await fetchStreams();
    setStreams(data);
  };

  const addStream = async () => {
    if (!name || !source) return alert("Fill stream name + source");

    await createStream({ name, source });
    setName(""); setSource("");
    loadStreams();
  };

  return (
    <div>
      <h2>Active Streams</h2>

      <div style={{ marginBottom: 20 }}>
        <input
          placeholder="Stream Name"
          value={name}
          onChange={e => setName(e.target.value)}
          style={{ padding: 5 }}
        />
        <input
          placeholder="Video Source / URL"
          value={source}
          onChange={e => setSource(e.target.value)}
          style={{ marginLeft: 5, padding: 5 }}
        />
        <button onClick={addStream} style={{ marginLeft: 5 }}>Add Stream</button>
      </div>

      <div>
        {streams.map(stream => (
          <StreamCard key={stream.id} stream={stream} />
        ))}
      </div>
    </div>
  );
}
