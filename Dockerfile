FROM astral-sh/uv:python3.12-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY api/ ./api/
COPY db/ ./db/
COPY utils/ ./utils/
COPY main.py .

RUN mkdir -p ./data/logs

EXPOSE 8080

CMD ["uv", "run", "main.py"]
