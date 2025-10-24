# Multi-stage build for OBCMS production optimization
# Stage 1: Node.js - Build Tailwind CSS assets
FROM node:18-alpine as node-builder

WORKDIR /app

# Copy package files and install Node.js dependencies
COPY package.json package-lock.json ./
# Install full dependency set (dev deps required for Tailwind/PostCSS build)
RUN npm ci

# Copy Tailwind configuration and source CSS
COPY tailwind.config.js postcss.config.js ./
COPY src/static/ src/static/
# Copy templates so Tailwind can scan for class names
COPY src/templates/ src/templates/

# Build production CSS with Tailwind
RUN npm run build:css && \
    # Verify CSS was built successfully
    test -f src/static/css/output.css && \
    echo "✓ Tailwind CSS built successfully: $(wc -c < src/static/css/output.css) bytes" || \
    (echo "✗ ERROR: Tailwind CSS build failed - output.css not found" && exit 1)

# Stage 2: Python Base - Common dependencies
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies including curl for healthchecks and libmagic for MIME validation
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies with aggressive cleanup
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt && \
    pip cache purge && \
    find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local -type f -name "*.pyc" -delete && \
    rm -rf /tmp/* /var/tmp/*

# Stage 3: Development
FROM base as development
RUN pip install -r requirements/development.txt
USER app

# Stage 4: Production - Combine Python app + compiled CSS
FROM base as production

# CRITICAL: Set production settings module to protect ad-hoc container launches
# This prevents CSRF 403 errors when containers run without docker-compose env vars
ENV DJANGO_SETTINGS_MODULE=obc_management.settings.production

# Copy application code
COPY --chown=app:app . /app/

# Copy compiled CSS from node-builder stage
COPY --from=node-builder --chown=app:app /app/src/static/css/output.css /app/src/static/css/output.css

# NOTE: Docker HEALTHCHECK disabled in favor of Kubernetes/Sevalla readiness probes
# Kubernetes handles container health monitoring through:
# - /ready/ endpoint for readiness probe
# - /health/ endpoint for liveness probe
# Having both Docker HEALTHCHECK and Kubernetes probes can cause conflicts in deployment
# For local Docker development, use: docker-compose ps to monitor container status

USER app

# Create staticfiles directory (collectstatic runs in Procfile release phase)
# This prevents Django startup warnings about missing directory
RUN mkdir -p /app/src/staticfiles

# Use gunicorn with production configuration file
# gunicorn.conf.py automatically reads PORT env var (Sevalla injects this)
# Note: collectstatic is handled by Procfile release phase, not here
CMD ["gunicorn", "--chdir", "src", "--config", "/app/gunicorn.conf.py", "obc_management.wsgi:application"]
