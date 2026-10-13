# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.12

# ---------- Stage 1: builder ----------
FROM python:${PYTHON_VERSION}-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /usr/local/bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Манифесты для кеширования зависимостей
COPY pyproject.toml uv.lock ./

# Prod-зависимости, lock обязателен, проект не ставим
RUN uv sync --no-dev --no-install-project --frozen

# ---------- Stage 2: runtime ----------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_PORT=8000 \
    DEBUG=false

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user с фиксированным uid=1000
RUN groupadd --system --gid 1000 storcard \
    && useradd --system --uid 1000 --gid storcard --create-home storcard

WORKDIR /app

# venv из builder + код приложения
COPY --from=builder /opt/venv /opt/venv
COPY --chown=storcard:storcard . .

# Каталог для данных и его права
RUN mkdir -p /app/data/logs /app/data/media \
    && chown -R storcard:storcard /app/data

USER storcard

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${APP_PORT}/status" || exit 1

# Запускаем uvicorn напрямую (без reload, exec-форма, PID 1)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${APP_PORT:-8000} --log-level warning"]