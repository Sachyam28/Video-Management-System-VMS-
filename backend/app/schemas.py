from pydantic import BaseModel
from typing import Optional

class StreamCreate(BaseModel):
    name: str
    source: str

class ModelToggle(BaseModel):
    model_name: str
    enabled: bool
