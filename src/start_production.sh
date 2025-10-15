#!/bin/bash
# OBCMS/BMMS Production Startup Script
# Optimized for 44 BARMM Ministries, Offices, and Agencies

set -e

echo "🚀 Starting OBCMS/BMMS Production Server..."
echo "============================================="

# Environment Validation
echo "🔍 Validating production environment..."

# Check Django settings module
if [ "$DJANGO_SETTINGS_MODULE" != "obc_management.settings.production" ]; then
    echo "❌ ERROR: DJANGO_SETTINGS_MODULE must be set to 'obc_management.settings.production'"
    echo "   Current value: $DJANGO_SETTINGS_MODULE"
    exit 1
fi

# Check critical production variables
if [ -z "$SECRET_KEY" ] || [[ "$SECRET_KEY" == *"django-insecure"* ]]; then
    echo "❌ ERROR: SECRET_KEY must be set to a secure value in production"
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "❌ ERROR: ALLOWED_HOSTS must be set in production"
    exit 1
fi

if [ -z "$CSRF_TRUSTED_ORIGINS" ]; then
    echo "❌ ERROR: CSRF_TRUSTED_ORIGINS must be set in production"
    exit 1
fi

echo "✅ Environment validation passed"

# Database Migration Check
echo "📊 Running Django system checks..."
python manage.py check --deploy

echo "🔄 Applying database migrations..."
python manage.py migrate --no-input

echo "📁 Collecting static files..."
python manage.py collectstatic --no-input --clear

# BMMS Mode Check
echo "🏛️  Checking BMMS configuration..."
python manage.py shell << 'EOF'
from obc_management.settings.bmms_config import BMMSMode
from django.conf import settings

print(f"BMMS Mode: {settings.BMMS_MODE}")
print(f"Multi-tenant: {settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT']}")
print(f"Organization Switching: {settings.RBAC_SETTINGS['ALLOW_ORGANIZATION_SWITCHING']}")
EOF

# AI Services Check
echo "🤖 Checking AI services configuration..."
python manage.py shell << 'EOF'
from django.conf import settings

print(f"AI Enabled: {getattr(settings, 'AI_ENABLED', False)}")
print(f"Google API Key Configured: {'Yes' if settings.GOOGLE_API_KEY else 'No'}")
print(f"Embedding Model: {getattr(settings, 'EMBEDDING_MODEL', 'Not configured')}")
EOF

# Performance Optimization
echo "⚡ Optimizing database connections..."
python manage.py shell << 'EOF'
from django.db import connection
from django.core.cache import cache

# Test database connection
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print("✅ Database connection successful")

# Test cache connection
try:
    cache.set('health_check', 'ok', 60)
    cache_result = cache.get('health_check')
    if cache_result == 'ok':
        print("✅ Cache connection successful")
    else:
        print("⚠️  Cache connection issue detected")
except Exception as e:
    print(f"⚠️  Cache connection failed: {e}")
EOF

# Start Gunicorn
echo "🌐 Starting Gunicorn production server..."
echo "Configuration: gunicorn.conf.py"
echo "Workers: $(python -c 'import multiprocessing; print(max(4, (2 * multiprocessing.cpu_count()) + 1))')"
echo "Port: 8000"
echo "============================================="

# Set environment variables for Gunicorn
export GUNICORN_LOG_LEVEL="info"

# Start Gunicorn with production configuration
exec gunicorn --config gunicorn.conf.py obc_management.wsgi:application