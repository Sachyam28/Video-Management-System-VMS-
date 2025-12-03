from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Stream(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    source: str  # e.g., file path, rtsp:// url, folder path
    active: bool = True

class InferenceResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stream_id: int
    model_name: str
    timestamp: datetime
    result_json: str  # store JSON as string
