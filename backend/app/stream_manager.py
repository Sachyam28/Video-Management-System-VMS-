import cv2
import asyncio
import threading, time, json, datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from sqlmodel import select

from .ai_models import MODEL_REGISTRY
from .db import get_session
from .models import InferenceResult, Stream


class StreamWorker:
    def __init__(self, stream_id: int, source: str, name: str, broadcaster=None):
        self.stream_id = stream_id
        self.source = source
        self.name = name
        self.broadcaster = broadcaster

        self.capture = None
        self.stop_event = threading.Event()
        self.enabled_models = {}  # model_name -> model instance
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()

        # 🔴 NEW: keep latest encoded jpeg for thumbnail
        self.last_jpeg = None

    def start(self):
        print(f"[StreamWorker] Starting stream {self.stream_id} ({self.name}) from source: {self.source}")
        self.capture = cv2.VideoCapture(self.source)
        t = threading.Thread(target=self._read_loop, daemon=True)
        t.start()

    def stop(self):
        print(f"[StreamWorker] Stopping stream {self.stream_id}")
        self.stop_event.set()
        if self.capture:
            try:
                self.capture.release()
            except Exception:
                pass

    def enable_model(self, model_name):
        cls = MODEL_REGISTRY.get(model_name)
        if not cls:
            raise ValueError(f"Unknown model: {model_name}")
        with self.lock:
            self.enabled_models[model_name] = cls()
        print(f"[StreamWorker] Enabled model '{model_name}' for stream {self.stream_id}")

    def disable_model(self, model_name):
        with self.lock:
            if model_name in self.enabled_models:
                del self.enabled_models[model_name]
        print(f"[StreamWorker] Disabled model '{model_name}' for stream {self.stream_id}")

    def _read_loop(self):
        while not self.stop_event.is_set():
            if not self.capture or not self.capture.isOpened():
                print(f"[StreamWorker] Capture not opened for stream {self.stream_id}, retrying...")
                time.sleep(1)
                self.capture = cv2.VideoCapture(self.source)
                continue

            ret, frame = self.capture.read()

            if not ret:
                # End of file or read error – restart the video for testing
                print(f"[StreamWorker] No frame for stream {self.stream_id}, restarting file...")
                try:
                    self.capture.release()
                except Exception:
                    pass
                time.sleep(0.5)
                self.capture = cv2.VideoCapture(self.source)
                continue

            # 🔴 NEW: update thumbnail (latest frame as JPEG)
            try:
                ok, buf = cv2.imencode(".jpg", frame)
                if ok:
                    with self.lock:
                        self.last_jpeg = buf.tobytes()
            except Exception as e:
                print(f"[StreamWorker] Thumbnail encode error for stream {self.stream_id}: {e}")

            # Submit frame to models
            with self.lock:
                models = list(self.enabled_models.items())

            if not models:
                # No models enabled – just sleep a bit
                time.sleep(0.05)
                continue

            for name, model in models:
                self.executor.submit(self._run_model, name, model, frame)

            # throttle ~20 FPS
            time.sleep(0.05)

    def _run_model(self, name, model, frame):
        try:
            # --------------------------
            # RUN MODEL INFERENCE
            # --------------------------
            res = model.predict(frame)
            print(f"[StreamWorker] Stream {self.stream_id} model '{name}' produced result: {res}")
    
            # --------------------------
            # ALERT LOGIC
            # --------------------------
            alert_flag = False
            if isinstance(res, dict) and "detections" in res:
                for det in res["detections"]:
                    if det.get("score", 0) > 0.60:
                        alert_flag = True
                        break
                    
            res["alert"] = alert_flag
    
            # --------------------------
            # STORE RESULT IN DATABASE
            # --------------------------
            session = get_session()
            ir = InferenceResult(
                stream_id=self.stream_id,
                model_name=name,
                timestamp=datetime.datetime.utcnow(),
                result_json=json.dumps(res),
            )
            session.add(ir)
            session.commit()
            session.close()
    
            # --------------------------
            # WEBSOCKET BROADCAST (SAFE)
            # --------------------------
            if self.broadcaster:
                event = {
                    "type": "inference",
                    "stream_id": self.stream_id,
                    "model": name,
                    "alert": alert_flag,
                    "result": res,
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                }
    
                import asyncio
    
                try:
                    # Try to get the running event loop
                    loop = asyncio.get_running_loop()
    
                    # Check if there are WebSocket clients connected
                    # broadcaster is a wrapper -> it exposes broadcaster_obj.connections
                    if hasattr(self.broadcaster, "__self__") and hasattr(self.broadcaster.__self__, "connections"):
                        if len(self.broadcaster.__self__.connections) == 0:
                            return  # no clients → skip broadcast
    
                    # Schedule WebSocket send safely
                    loop.call_soon_threadsafe(asyncio.create_task, self.broadcaster(event))
    
                except RuntimeError:
                    # No event loop → skip silently
                    pass
                
        except Exception as e:
            print("Model error", e)


class StreamManager:
    def __init__(self, broadcaster=None):
        self.workers: Dict[int, StreamWorker] = {}
        self.broadcaster = broadcaster

    def load_streams_from_db(self, session):
        q = session.exec(select(Stream)).all()
        for s in q:
            print(f"[StreamManager] Loading stream from DB: {s.id} {s.name} {s.source}")
            self.add_stream(s.id, s.source, s.name, start=False)

    def add_stream(self, stream_id: int, source: str, name: str, start: bool = True):
        print(f"[StreamManager] Adding stream {stream_id} with source={source}")
        w = StreamWorker(stream_id, source, name, broadcaster=self.broadcaster)
        self.workers[stream_id] = w
        if start:
            w.start()
        return w

    def remove_stream(self, stream_id: int):
        print(f"[StreamManager] Removing stream {stream_id}")
        w = self.workers.pop(stream_id, None)
        if w:
            w.stop()

    def get_worker(self, stream_id: int):
        return self.workers.get(stream_id)
