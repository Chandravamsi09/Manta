# Multi-stage production build for Manta ML Platform
FROM python:3.11-slim as base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY manta ./manta

RUN pip install --upgrade pip && \
    pip install -e .

EXPOSE 8000 50051

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "manta.gateway.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
