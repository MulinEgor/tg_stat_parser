FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    binutils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.7 /uv /uvx /bin/

COPY . /app
WORKDIR /app

RUN uv sync
RUN uv run pyinstaller --onefile src/main.py
  
ENV PATH="/app/.venv/bin:$PATH"
