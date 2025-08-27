FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.3

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies only first (for better caching)
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# App code
COPY . .

# Install the backend package itself (core, simulation, optimization modules)
RUN poetry install --only=main

# Ensure charts directory exists for runtime-generated images
RUN mkdir -p simulation/charts

# Create non-root user and fix permissions (charts must be writable)
RUN adduser --disabled-password --gecos "" appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Align with app route (use PORT if provided by platform like Cloud Run)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD sh -c 'curl -fsS http://localhost:${PORT:-8000}/ || exit 1'

# Use PORT if provided (Cloud Run), default to 8000 locally
CMD ["sh", "-c", "poetry run uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]