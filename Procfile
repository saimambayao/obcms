# Sevalla Procfile for OBCMS Deployment
# Defines how to run web server, background workers, and release tasks

# Release Phase: Run database migrations and collect static files
# Note: This runs automatically before each deployment on Railway
# Migrations: Updates database schema to match current code
# Static files: Collected during Docker build but also here as backup
# Railway timeout is generous (~30+ minutes), so this is safe
release: cd src && python manage.py migrate --noinput --settings obc_management.settings.production && python manage.py collectstatic --noinput

# Web Process: Gunicorn WSGI server
# IMPORTANT: Must bind to $PORT (auto-injected by Railway)
# Static files: Served by WhiteNoise (using pre-collected staticfiles from Docker build)
web: cd src && gunicorn obc_management.wsgi:application --bind 0.0.0.0:$PORT --workers=${GUNICORN_WORKERS:-4} --threads=${GUNICORN_THREADS:-2} --worker-class=${GUNICORN_WORKER_CLASS:-gthread} --log-level=${GUNICORN_LOG_LEVEL:-info} --access-logfile - --error-logfile -

# Worker Process: Celery background task processor
# Scale workers independently in Sevalla dashboard
worker: cd src && celery -A obc_management worker --loglevel=info --concurrency=2

# Beat Process: Celery periodic task scheduler (optional)
# Uncomment if you have periodic tasks configured
# beat: cd src && celery -A obc_management beat --loglevel=info
