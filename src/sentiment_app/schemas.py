# schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PredictIn(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class PredictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    label: str
    score: float
    model_version: str
    created_at: datetime
