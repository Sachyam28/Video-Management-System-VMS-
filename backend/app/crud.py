from .models import Stream, InferenceResult
from .db import get_session
from sqlmodel import select
import json

def create_stream(name, source):
    session = get_session()
    s = Stream(name=name, source=source)
    session.add(s)
    session.commit()
    session.refresh(s)
    session.close()
    return s

def list_streams():
    session = get_session()
    res = session.exec(select(Stream)).all()
    session.close()
    return res

def get_recent_results(stream_id, limit=50):
    session = get_session()
    q = session.exec(select(InferenceResult).where(InferenceResult.stream_id==stream_id).order_by(InferenceResult.timestamp.desc()).limit(limit)).all()
    session.close()
    # parse JSON
    for r in q:
        r.result_json = json.loads(r.result_json)
    return q
