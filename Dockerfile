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

# Set environment variables for maximum compatibility and performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    gettext \
    curl \
    libmagic1 \
    && pip install --upgrade pip setuptools wheel \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt \
    && find /usr/local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local -type f -name "*.pyc" -delete \
    && rm -rf /tmp/* /var/tmp/*

# Stage 3: Development
FROM base as development
RUN pip install -r requirements/development.txt
USER nobody

# Stage 4: Production - Combine Python app + compiled CSS
FROM python:3.12-slim as production

# Accept build arguments for Django settings validation
# These are passed via: docker build --build-arg SECRET_KEY=... --build-arg ALLOWED_HOSTS=...
ARG SECRET_KEY
ARG ALLOWED_HOSTS
ARG CSRF_TRUSTED_ORIGINS

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=obc_management.settings.production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    libmagic1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy pre-compiled Python dependencies from base stage
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=nobody:nobody . /app/

# Copy compiled CSS from node-builder stage
COPY --from=node-builder --chown=nobody:nobody /app/src/static/css/output.css /app/src/static/css/output.css

# NOTE: Docker HEALTHCHECK disabled in favor of Railway health checks
# Railway uses built-in health probe configuration
# For local Docker development, use: docker-compose ps to monitor container status

# Collect static files during Docker build with environment variables
# Build arguments (SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS) are passed at build time
# This ensures staticfiles/ is pre-baked into the image before runtime
RUN SECRET_KEY=${SECRET_KEY} \
    ALLOWED_HOSTS=${ALLOWED_HOSTS} \
    CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS} \
    DJANGO_SETTINGS_MODULE=obc_management.settings.production \
    python src/manage.py collectstatic --noinput && \
    echo "✓ Static files collected successfully: $(du -sh src/staticfiles/ | cut -f1)" || \
    (echo "✗ ERROR: Static files collection failed" && exit 1)

# Run as unprivileged user
USER nobody

# Use gunicorn with production configuration file
# gunicorn.conf.py automatically reads PORT env var (Railway injects this)
# Static files are now pre-collected in the Docker image
CMD ["gunicorn", "--chdir", "src", "--config", "/app/gunicorn.conf.py", "obc_management.wsgi:application"]
