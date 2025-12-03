import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Streams
export const fetchStreams = () =>
  API.get("/streams").then((res) => res.data);

export const createStream = ({ name, source }) =>
  API.post("/streams", { name, source }).then((res) => res.data);

export async function deleteStream(stream_id) {
  await fetch(`http://localhost:8000/streams/${stream_id}`, {
    method: "DELETE",
  });
}


// Models
export const toggleModel = (stream_id, model_name, enabled) =>
  API.post(`/streams/${stream_id}/models`, { model_name, enabled }).then(res => res.data);

// Inference results
export const fetchResults = (stream_id) =>
  API.get(`/streams/${stream_id}/results`).then((res) => res.data);
