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

# Collect static files BEFORE running as unprivileged user
# (Django collectstatic needs write permissions to staticfiles directory)
# This ensures static files are available immediately when container starts
# WARNING: Must run as root before switching to unprivileged user
# NOTE: Use development settings for collectstatic since production requires
#       environment variables that aren't available during Docker build
# Provide minimal environment variables just for the collectstatic build step
# SECRET_KEY must be at least 50 characters (temporary build-only key)
RUN cd /app/src && SECRET_KEY="django-insecure-build-only-temporary-key-for-docker-build-12345" \
    python manage.py collectstatic --noinput --settings=obc_management.settings.development && \
    echo "✓ Static files collected successfully"

# Verify critical static files were collected
RUN test -f /app/src/staticfiles/css/output.css && \
    echo "✓ Tailwind CSS found in staticfiles" || \
    (echo "✗ ERROR: Tailwind CSS not found in staticfiles" && exit 1)

RUN test -f /app/src/staticfiles/favicon.svg && \
    echo "✓ favicon.svg found in staticfiles" || \
    (echo "✗ ERROR: favicon.svg not found in staticfiles" && exit 1)

# Set appropriate permissions on staticfiles directory
RUN chmod -R 755 /app/src/staticfiles

# Run as unprivileged user
USER nobody

# Use gunicorn with production configuration file
# gunicorn.conf.py automatically reads PORT env var (Railway injects this)
# Static files are now pre-collected in the Docker image
CMD ["gunicorn", "--chdir", "src", "--config", "/app/gunicorn.conf.py", "obc_management.wsgi:application"]
