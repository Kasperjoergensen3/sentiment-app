# models.py
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Prediction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(max_length=1000)
    label: str = Field(max_length=20)
    score: float
    model_version: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
