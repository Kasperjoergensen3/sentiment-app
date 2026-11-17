"""Train the sentiment model and write models/sentiment.joblib + models/sentiment.json.

Run with:  uv run python -m sentiment_app.ml.train --version v1
"""

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline

SEED = 42  # one seed, used everywhere randomness appears


def git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        )
        return out.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/reviews.csv"))
    parser.add_argument("--out", type=Path, default=Path("models/sentiment.joblib"))
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()

    with args.data.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    texts = [r["text"] for r in rows]
    labels = [r["label"] for r in rows]

    pipeline = make_pipeline(
        TfidfVectorizer(),
        LogisticRegression(max_iter=1000, random_state=SEED),
    )
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_accuracy = cross_val_score(pipeline, texts, labels, cv=folds).mean()
    pipeline.fit(texts, labels)  # the shipped model is trained on all rows

    metadata = {
        "version": args.version,
        "trained_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_sha": git_sha(),
        "data_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "sklearn_version": sklearn.__version__,
        "seed": SEED,
        "n_samples": len(rows),
        "cv_accuracy": round(float(cv_accuracy), 3),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "version": args.version}, args.out)
    args.out.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
