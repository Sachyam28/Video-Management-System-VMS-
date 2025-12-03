from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db, get_session
from .crud import create_stream, list_streams, get_recent_results
from .stream_manager import StreamManager
from .schemas import StreamCreate, ModelToggle
from fastapi.responses import Response
from .models import Stream

import asyncio

app = FastAPI(title="RoadVision VMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# simple broadcaster implementation
class Broadcaster:
    def __init__(self):
        self.connections = set()
    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
    def disconnect(self, websocket:WebSocket):
        self.connections.discard(websocket)
    async def broadcast(self, message):
        websockets = list(self.connections)
        for ws in websockets:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)

broadcaster = Broadcaster()

# create a helper to pass to stream manager that schedules broadcast
def broadcaster_fn(event):
    # schedule coroutine
    loop = asyncio.get_running_loop()
    loop.call_soon_threadsafe(asyncio.create_task, broadcaster.broadcast(event))

manager = StreamManager(broadcaster=broadcaster_fn)

# load existing streams from DB
session = get_session()
manager.load_streams_from_db(session)
session.close()

@app.post("/streams")
def add_stream(s: StreamCreate):
    st = create_stream(s.name, s.source)
    manager.add_stream(st.id, st.source, st.name, start=True)
    return {"msg":"created", "stream": st}

@app.get("/streams")
def api_list_streams():
    return list_streams()

@app.delete("/streams/{stream_id}")
def delete_stream(stream_id: int):
    session = get_session()

    # Remove stream from DB
    db_stream = session.get(Stream, stream_id)
    if not db_stream:
        raise HTTPException(404, "Stream not found")

    session.delete(db_stream)
    session.commit()

    # Stop worker
    manager.remove_stream(stream_id)

    return {"msg": "stream deleted"}


@app.post("/streams/{stream_id}/models")
def toggle_model(stream_id: int, body: ModelToggle):
    w = manager.get_worker(stream_id)
    if not w:
        raise HTTPException(404, "stream not running")
    if body.enabled:
        w.enable_model(body.model_name)
    else:
        w.disable_model(body.model_name)
    return {"msg":"ok", "enabled_models": list(w.enabled_models.keys())}

@app.get("/streams/{stream_id}/results")
def stream_results(stream_id: int, limit:int = 20):
    return get_recent_results(stream_id, limit=limit)

@app.get("/streams/{stream_id}/thumbnail")
def get_thumbnail(stream_id: int):
    w = manager.get_worker(stream_id)
    if not w:
        raise HTTPException(404, "stream not running")

    # grab latest jpeg
    with w.lock:
        jpeg_bytes = w.last_jpeg

    if not jpeg_bytes:
        # no frame yet
        raise HTTPException(404, "no thumbnail available yet")

    return Response(content=jpeg_bytes, media_type="image/jpeg")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            # keep connection open; if client sends messages, ignore or handle
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
