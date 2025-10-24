#!/bin/bash
# Docker entrypoint script for OBCMS
# Runs database migrations then starts the web server

set -e

echo "🚀 Starting OBCMS..."

# Change to src directory
cd /app/src

echo "🗄️  Running database migrations..."
python manage.py migrate --noinput --settings obc_management.settings.production

echo "✅ Migrations completed successfully"
echo "🌐 Starting gunicorn web server..."

# Execute gunicorn with the passed arguments
exec gunicorn --config /app/gunicorn.conf.py obc_management.wsgi:application "$@"
