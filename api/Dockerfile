FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Only curl for healthcheck; drop compilers to keep image small
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# Leverage layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Ensure charts directory exists for runtime-generated images
RUN mkdir -p charts

# Create non-root user and fix permissions (charts must be writable)
RUN adduser --disabled-password --gecos "" appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Align with app route (use PORT if provided by platform like Cloud Run)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD sh -c 'curl -fsS http://localhost:${PORT:-8000}/ || exit 1'

# Use PORT if provided (Cloud Run), default to 8000 locally
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]