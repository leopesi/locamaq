# ──────────────────────────────────────────────
# LocaMaq — Production Dockerfile (Multi-stage)
# ──────────────────────────────────────────────

# Stage 1: Dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim

# WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data /app/media /app/staticfiles /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Non-root user
RUN useradd -m -r locamaq && chown -R locamaq:locamaq /app
USER locamaq

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/accounts/login/ || exit 1

# Gunicorn with optimized settings
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "120"]
