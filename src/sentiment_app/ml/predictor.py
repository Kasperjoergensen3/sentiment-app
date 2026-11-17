from dataclasses import dataclass
from pathlib import Path

import joblib


@dataclass(frozen=True)
class Result:
    label: str
    score: float


class SentimentModel:
    """Loads the model artifact once and serves predictions."""

    def __init__(self, path: Path) -> None:
        bundle = joblib.load(path)  # only ever load artifacts you produced yourself
        self.pipeline = bundle["pipeline"]
        self.version: str = bundle["version"]

    def predict(self, text: str) -> Result:
        proba = self.pipeline.predict_proba([text])[0]
        best = int(proba.argmax())
        return Result(label=str(self.pipeline.classes_[best]), score=float(proba[best]))
