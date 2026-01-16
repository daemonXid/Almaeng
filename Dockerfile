# ============================================
# 😈 ALMAENG Production Dockerfile
# ============================================
# Multi-stage build with Rust support
# Uses: Python 3.12 + Rust + bun + Granian
# ============================================

# --- Stage 1: Frontend Build ---
FROM oven/bun:1 AS frontend-builder

WORKDIR /app

# Copy frontend dependencies
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Copy frontend source and build
COPY tailwind.config.js ./
COPY backend/static/ backend/static/
COPY backend/templates/ backend/templates/
COPY backend/domains/ backend/domains/

RUN bun run build

# --- Stage 2: Python Build ---
FROM python:3.12-slim-bookworm AS python-builder

WORKDIR /app

# Install build dependencies (no Rust needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Install all dependencies
RUN uv sync --frozen --no-dev

# --- Stage 3: Production Runtime ---
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=python-builder /app/.venv /app/.venv

# Copy application code
COPY backend/ backend/
COPY main.py ./

# Copy built frontend assets
COPY --from=frontend-builder /app/backend/static/dist/ backend/static/dist/
COPY --from=frontend-builder /app/backend/static/css/output.css backend/static/css/output.css

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app:/app/backend:/app/backend/domains
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV DEBUG=false

# Collect static files
RUN python backend/manage.py collectstatic --noinput

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live/ || exit 1

# Run with Granian (Rust ASGI)
CMD ["granian", "--interface", "asgi", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
