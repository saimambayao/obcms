# Sevalla Procfile for OBCMS Deployment
# Defines how to run web server, background workers, and release tasks

# Release Phase: Collect static files for WhiteNoise serving
# Railway timeout is generous (~30+ minutes), so this is safe
# Note: Migrations must be run manually via Railway CLI before first deployment
#   railway run python src/manage.py migrate --noinput
release: cd src && python manage.py collectstatic --noinput

# Web Process: Gunicorn WSGI server
# IMPORTANT: Must bind to $PORT (auto-injected by Railway)
# Static files: Served by WhiteNoise (using collected staticfiles from release phase)
web: cd src && gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers=${GUNICORN_WORKERS:-4} --threads=${GUNICORN_THREADS:-2} --worker-class=${GUNICORN_WORKER_CLASS:-gthread} --log-level=${GUNICORN_LOG_LEVEL:-info} --access-logfile - --error-logfile -

# Worker Process: Celery background task processor
# Scale workers independently in Sevalla dashboard
worker: cd src && celery -A obc_management worker --loglevel=info --concurrency=2

# Beat Process: Celery periodic task scheduler (optional)
# Uncomment if you have periodic tasks configured
# beat: cd src && celery -A obc_management beat --loglevel=info
