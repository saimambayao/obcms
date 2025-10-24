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

# Collect static files during Docker build
# We set temporary environment variables just for the build step.
# These are NOT included in the final container runtime.
# Production settings require these for validation, but they're only used during collectstatic.
RUN set -e && \
    # Set temporary environment variables for collectstatic validation
    export SECRET_KEY="django-build-temporary-$(head -c 40 /dev/urandom | base64)" && \
    export ALLOWED_HOSTS="localhost,127.0.0.1,.internal" && \
    export CSRF_TRUSTED_ORIGINS="https://localhost" && \
    export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend" && \
    # Run collectstatic with production settings
    cd /app/src && python manage.py collectstatic --noinput --clear && \
    # Verify static files were collected
    test -d /app/src/staticfiles && \
    echo "✓ Static files collected successfully" && \
    # Verify key static files exist
    test -f /app/src/staticfiles/css/output.css && \
    echo "✓ Tailwind CSS included in staticfiles" || \
    (echo "✗ ERROR: collectstatic failed or staticfiles directory not created" && exit 1)

# NOTE: Docker HEALTHCHECK disabled in favor of Railway health checks
# Railway uses built-in health probe configuration
# For local Docker development, use: docker-compose ps to monitor container status

# WhiteNoise middleware serves collected static files at runtime from src/staticfiles/
# Static files are pre-collected during Docker build to avoid relying on release phase
# (Railway doesn't reliably execute release phases)

# Run as unprivileged user (must be before CMD to maintain proper permissions)
USER nobody

# Use gunicorn with production configuration file
# gunicorn.conf.py automatically reads PORT env var (Railway injects this)
# Static files served by WhiteNoise from src/staticfiles/ (pre-collected during Docker build)
CMD ["gunicorn", "--chdir", "src", "--config", "/app/gunicorn.conf.py", "obc_management.wsgi:application"]
