# main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sentiment_app.config import get_settings
from sentiment_app.db import init_db
from sentiment_app.ml.predictor import SentimentModel
from sentiment_app.routes import router

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # creates tables if missing (swap for Alembic migrations later)
    app.state.model = SentimentModel(get_settings().classifier_path)  # load once at startup
    yield


app = FastAPI(title="Sentiment App", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}
