# Sevalla Procfile for OBCMS Deployment
# Defines how to run web server, background workers, and release tasks

# Release Phase: TEMPORARILY DISABLED for debugging
# TODO: Re-enable after successful deployment
# release: cd src && python manage.py migrate --noinput && python manage.py collectstatic --noinput

# Web Process: Gunicorn WSGI server
# IMPORTANT: Must bind to $PORT (auto-injected by Sevalla)
# Static files: Served by WhiteNoise (no collectstatic needed for testing)
web: cd src && python manage.py migrate --noinput && gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers=${GUNICORN_WORKERS:-4} --threads=${GUNICORN_THREADS:-2} --worker-class=${GUNICORN_WORKER_CLASS:-gthread} --log-level=${GUNICORN_LOG_LEVEL:-info} --access-logfile - --error-logfile -

# Worker Process: Celery background task processor
# Scale workers independently in Sevalla dashboard
worker: cd src && celery -A obc_management worker --loglevel=info --concurrency=2

# Beat Process: Celery periodic task scheduler (optional)
# Uncomment if you have periodic tasks configured
# beat: cd src && celery -A obc_management beat --loglevel=info
