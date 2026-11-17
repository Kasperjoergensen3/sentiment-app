import json
from pathlib import Path

import pytest

from sentiment_app.ml.predictor import SentimentModel

MODEL_PATH = Path("models/sentiment.joblib")
MIN_CV_ACCURACY = 0.75  # raise this as your real dataset grows


@pytest.fixture(scope="module")
def model():
    return SentimentModel(MODEL_PATH)


def test_model_meets_quality_bar():
    metadata = json.loads(MODEL_PATH.with_suffix(".json").read_text())
    assert metadata["cv_accuracy"] >= MIN_CV_ACCURACY


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("I love it", "positive"),
        ("Great product, highly recommend", "positive"),
        ("It broke, waste of money", "negative"),
        ("Very disappointed", "negative"),
    ],
)
def test_golden_examples(model, text, expected):
    assert model.predict(text).label == expected


def test_prediction_is_deterministic(model):
    assert model.predict("great value") == model.predict("great value")
