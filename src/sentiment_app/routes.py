# routes.py
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session, col, select

from sentiment_app.db import get_session
from sentiment_app.ml.predictor import SentimentModel
from sentiment_app.models import Prediction
from sentiment_app.schemas import PredictIn, PredictOut

router = APIRouter()


def get_model(request: Request) -> SentimentModel:
    return request.app.state.model


SessionDep = Annotated[Session, Depends(get_session)]
ModelDep = Annotated[SentimentModel, Depends(get_model)]


@router.post("/predict", response_model=PredictOut, status_code=201)
def predict(payload: PredictIn, session: SessionDep, model: ModelDep) -> Prediction:
    result = model.predict(payload.text)
    row = Prediction(
        text=payload.text,
        label=result.label,
        score=result.score,
        model_version=model.version,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.get("/predictions", response_model=list[PredictOut])
def list_predictions(
    session: SessionDep, limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[Prediction]:
    stmt = select(Prediction).order_by(col(Prediction.created_at).desc()).limit(limit)
    return list(session.exec(stmt))