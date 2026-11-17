# syntax=docker/dockerfile:1

# ---------- Stage 1: build the virtual environment ----------
    FROM python:3.13-slim AS builder
    COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

    ENV UV_COMPILE_BYTECODE=1 \
        UV_LINK_MODE=copy \
        UV_PYTHON_DOWNLOADS=never

    WORKDIR /app

    # Dependencies first: this layer stays cached until uv.lock or pyproject.toml change
    RUN --mount=type=cache,target=/root/.cache/uv \
        --mount=type=bind,source=uv.lock,target=uv.lock \
        --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
        uv sync --locked --no-install-project --no-dev

    # Then the project itself, installed as a regular (non-editable) package
    COPY . /app
    RUN --mount=type=cache,target=/root/.cache/uv \
        uv sync --locked --no-dev --no-editable

    # ---------- Stage 2: slim runtime image ----------
    FROM python:3.13-slim

    RUN useradd --create-home --uid 1000 appuser
    WORKDIR /app
    COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
    COPY --from=builder --chown=appuser:appuser /app/models /app/models
    RUN chown appuser:appuser /app

    ENV PATH="/app/.venv/bin:$PATH" \
        PYTHONUNBUFFERED=1 \
        APP_ENV=production

    USER appuser
    EXPOSE 8000

    # Render injects $PORT; locally it defaults to 8000. "exec" lets uvicorn receive shutdown signals.
    CMD ["sh", "-c", "exec uvicorn sentiment_app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
