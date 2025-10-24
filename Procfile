# Sevalla Procfile for OBCMS Deployment
# Defines how to run web server, background workers, and release tasks

# NOTE: This Procfile is for reference/compatibility only.
# Railway uses Docker for deployments, not the Procfile.
# Database migrations and static file collection are handled by:
#   - Docker entrypoint script: docker-entrypoint.sh (runs migrations on startup)
#   - Docker build: Collects static files during image build
# See Dockerfile and docker-entrypoint.sh for implementation details.

# Web Process: Gunicorn WSGI server
# In Docker: Runs via docker-entrypoint.sh which handles migrations first
# IMPORTANT: Must bind to $PORT (auto-injected by Railway)
# Static files: Served by WhiteNoise (using pre-collected staticfiles from Docker build)
web: cd src && gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers=${GUNICORN_WORKERS:-4} --threads=${GUNICORN_THREADS:-2} --worker-class=${GUNICORN_WORKER_CLASS:-gthread} --log-level=${GUNICORN_LOG_LEVEL:-info} --access-logfile - --error-logfile -

# Worker Process: Celery background task processor
# Scale workers independently in Sevalla dashboard
worker: cd src && celery -A obc_management worker --loglevel=info --concurrency=2

# Beat Process: Celery periodic task scheduler (optional)
# Uncomment if you have periodic tasks configured
# beat: cd src && celery -A obc_management beat --loglevel=info
