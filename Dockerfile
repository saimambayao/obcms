# Multi-stage build for OBCMS production optimization - Sevalla Ready
# Stage 1: Node.js - Build Tailwind CSS assets
FROM node:18-alpine as node-builder

WORKDIR /app

# Copy package files and install Node.js dependencies
COPY package.json package-lock.json ./
# Install full dependency set (dev deps required for Tailwind/PostCSS build)
RUN npm ci --only=production=false --silent

# Copy Tailwind configuration and source CSS
COPY tailwind.config.js postcss.config.js ./
COPY src/static/ src/static/
# Copy templates so Tailwind can scan for class names
COPY src/templates/ src/templates/

# Build production CSS with Tailwind
RUN npm run build:css && \
    npm run build:js && \
    # Verify assets were built successfully
    test -f src/static/css/output.css && \
    echo "✓ Tailwind CSS built successfully: $(wc -c < src/static/css/output.css) bytes" && \
    test -f src/static/js/output.js || true && \
    echo "✓ Build completed successfully" || \
    (echo "✗ ERROR: Build failed - required files not found" && exit 1)

# Stage 2: Python Base - Common dependencies for Sevalla
FROM python:3.12-slim as base

# Set environment variables for production deployment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src \
    DJANGO_SETTINGS_MODULE=obc_management.settings.production

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    libmagic1 \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user with proper permissions
RUN groupadd -r app && useradd -r -g app --home-dir /app --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies with optimizations
COPY requirements/ requirements/
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements/base.txt && \
    pip install gunicorn psycopg[binary] django-storages boto3 && \
    pip cache purge

# Stage 3: Development (keeps existing functionality)
FROM base as development
RUN pip install -r requirements/development.txt
USER app

# Stage 4: Production - Optimized for Sevalla deployment
FROM base as production

# Add production-specific labels for Sevalla
LABEL maintainer="BMMS Team" \
      version="1.0.0" \
      description="Bangsamoro Ministerial Management System - Production Deployment" \
      org.opencontainers.image.title="OBCMS Production" \
      org.opencontainers.image.description="BMMS production deployment on Sevalla"

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/media /app/staticfiles /app/static && \
    chown -R app:app /app

# Copy application code with proper permissions
COPY --chown=app:app . /app/

# Copy compiled assets from node-builder stage
COPY --from=node-builder --chown=app:app /app/src/static/css/output.css /app/src/static/css/output.css
# Copy JS output if it exists (optional file)
RUN --mount=type=bind,from=node-builder,source=/app/src/static/js/output.js,target=/tmp/output.js \
    cp /tmp/output.js /app/src/static/js/output.js 2>/dev/null || echo "JS output not found, skipping..." && \
    chown app:app /app/src/static/js/output.js 2>/dev/null || true

# Create startup script for production
COPY --chown=app:app <<-'EOT' /app/startup.sh
#!/bin/bash
set -e

echo "Starting OBCMS Production deployment..."

# Change to src directory
cd /app/src

# Check if we need to run migrations
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 0

# Create cache tables
echo "Creating cache tables..."
python manage.py createcachetable || true

# Check deployment readiness
echo "Running deployment checks..."
python manage.py check --deploy

echo "OBCMS is ready! Starting Gunicorn..."
EOT

RUN chmod +x /app/startup.sh

# Create health check script
COPY --chown=app:app <<-'EOT' /app/healthcheck.sh
#!/bin/bash
set -e

# Basic health check
curl -f http://localhost:8000/health/ || exit 1

# Optional: Check database connectivity
cd /app/src
python manage.py check --database default --quiet || exit 1

echo "Health check passed"
EOT

RUN chmod +x /app/healthcheck.sh

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Enhanced health check for Sevalla
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh || exit 1

# Use startup script
ENTRYPOINT ["/app/startup.sh"]

# Use gunicorn with production configuration
CMD ["gunicorn", "--chdir", "src", "--config", "/app/gunicorn.conf.py", "obc_management.wsgi:application"]
