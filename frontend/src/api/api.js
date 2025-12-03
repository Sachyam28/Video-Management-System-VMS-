import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// -----------------------------
// STREAMS
// -----------------------------

export const fetchStreams = () =>
  API.get("/streams").then((res) => res.data);

export const createStream = ({ name, source }) =>
  API.post("/streams", { name, source }).then((res) => res.data);

export const deleteStream = (stream_id) =>
  API.delete(`/streams/${stream_id}`).then((res) => res.data);

// -----------------------------
// MODELS
// -----------------------------

export const toggleModel = (stream_id, model_name, enabled) =>
  API.post(`/streams/${stream_id}/models`, { model_name, enabled }).then(
    (res) => res.data
  );

// -----------------------------
// RESULTS
// -----------------------------

export const fetchResults = (stream_id) =>
  API.get(`/streams/${stream_id}/results`).then((res) => res.data);



export const fetchThumbnail = (stream_id) =>
  API.get(`/streams/${stream_id}/thumbnail`, {
    responseType: "blob",
  });
