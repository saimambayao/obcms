#!/bin/bash
# OBCMS/BMMS Production Environment Setup Script
# This script sets up the production environment for OBCMS/BMMS deployment

set -e

echo "🚀 OBCMS/BMMS Production Environment Setup"
echo "=========================================="

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ ERROR: manage.py not found. Please run this script from the src/ directory."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -n1)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ ERROR: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  WARNING: No virtual environment detected. Creating one..."

    # Create virtual environment
    if [ ! -d "../venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv ../venv
    fi

    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source ../venv/bin/activate
else
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
fi

# Install/update dependencies
echo "📦 Installing/updating dependencies..."

# Base requirements
if [ -f "requirements/base.txt" ]; then
    echo "Installing base requirements..."
    pip install --upgrade pip
    pip install -r requirements/base.txt
else
    echo "❌ ERROR: requirements/base.txt not found"
    exit 1
fi

# AI requirements
if [ -f "requirements/ai.txt" ]; then
    echo "Installing AI requirements..."
    pip install -r requirements/ai.txt
else
    echo "⚠️  WARNING: requirements/ai.txt not found. AI services may not be available."
fi

# Production requirements
if [ -f "requirements/production.txt" ]; then
    echo "Installing production requirements..."
    pip install -r requirements/production.txt
else
    echo "⚠️  WARNING: requirements/production.txt not found. Creating basic production requirements..."
    cat > requirements/production.txt << EOF
# Production dependencies for OBCMS/BMMS
gunicorn>=21.2.0
psycopg2-binary>=2.9.0
redis>=4.5.0
django-extensions>=3.2.0
whitenoise>=6.5.0
EOF
    pip install -r requirements/production.txt
fi

# Set up environment file
echo "📝 Setting up environment configuration..."

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "Creating .env file from template..."
    if [ -f "../.env.production" ]; then
        cp ../.env.production ../.env
        echo "✅ .env file created from .env.production template"
        echo "⚠️  IMPORTANT: Review and update ../.env with your production values!"
    else
        echo "❌ ERROR: .env.production template not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Generate secure SECRET_KEY if needed
echo "🔐 Checking security configuration..."

# Check if SECRET_KEY is set to default value
if grep -q "django-insecure" ../.env; then
    echo "⚠️  WARNING: Insecure SECRET_KEY detected. Generating new one..."

    # Generate new SECRET_KEY
    NEW_SECRET_KEY=$(python3 -c "
import secrets
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
secret = ''.join(secrets.choice(chars) for _ in range(50))
print(secret)
")

    # Update .env file
    sed -i.bak "s/SECRET_KEY=django-insecure.*/SECRET_KEY=$NEW_SECRET_KEY/" ../.env
    echo "✅ New secure SECRET_KEY generated and saved to .env"
    echo "📁 Original .env saved as .env.bak"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."

mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p backups

echo "✅ Directory structure created"

# Set permissions
echo "🔒 Setting file permissions..."

chmod 755 logs media staticfiles backups
chmod +x start_production.sh

echo "✅ Permissions set"

# Check database configuration
echo "🗄️  Checking database configuration..."

if grep -q "sqlite://" ../.env; then
    echo "⚠️  WARNING: SQLite database detected. Consider PostgreSQL for production."
    echo "   To migrate to PostgreSQL:"
    echo "   1. Install PostgreSQL: brew install postgresql (Mac) or apt-get install postgresql (Ubuntu)"
    echo "   2. Create database and user"
    echo "   3. Update DATABASE_URL in .env"
    echo "   4. Run database migration script"
else
    echo "✅ PostgreSQL configuration detected"
fi

# Run Django checks
echo "🔍 Running Django system checks..."

export DJANGO_SETTINGS_MODULE=obc_management.settings.production

python manage.py check --deploy --verbosity=2

# Check if migrations are needed
echo "🔄 Checking database migrations..."

python manage.py showmigrations --plan | grep -q "\[ \]" || {
    echo "📊 Applying database migrations..."
    python manage.py migrate --verbosity=2
}

# Collect static files
echo "📁 Collecting static files..."

python manage.py collectstatic --no-input --clear --verbosity=2

# Create superuser if doesn't exist
echo "👤 Checking for admin user..."

if python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    exit(1)
else:
    exit(0)
"; then
    echo "✅ Admin user exists"
else
    echo "⚠️  No admin user found. Creating default admin user..."
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.create_superuser(
    username='admin',
    email='admin@obcms.gov.ph',
    password='admin123456',
    first_name='System',
    last_name='Administrator'
)
print(f"✅ Admin user created: {admin.username}")
print("⚠️  IMPORTANT: Change the default password on first login!")
EOF
fi

# Test AI services configuration
echo "🤖 Testing AI services configuration..."

python manage.py shell << 'EOF'
from django.conf import settings
import sys

print("AI Configuration:")
print(f"  AI Enabled: {getattr(settings, 'AI_ENABLED', False)}")
print(f"  Google API Key: {'Configured' if settings.GOOGLE_API_KEY else 'Not configured'}")
print(f"  Embedding Model: {getattr(settings, 'EMBEDDING_MODEL', 'Not configured')}")

# Test embedding service import
try:
    from ai_assistant.services.embedding_service import EmbeddingService
    print("✅ EmbeddingService import successful")
except ImportError as e:
    print(f"⚠️  EmbeddingService import failed: {e}")
    print("   This is expected if AI dependencies are not yet installed")

# Test Gemini service import
try:
    from ai_assistant.services.gemini_service import GeminiService
    print("✅ GeminiService import successful")
except ImportError as e:
    print(f"⚠️  GeminiService import failed: {e}")
    print("   This is expected if AI dependencies are not yet installed")
EOF

# Test BMMS configuration
echo "🏛️  Testing BMMS configuration..."

python manage.py shell << 'EOF'
from django.conf import settings
from obc_management.settings.bmms_config import BMMSMode

print("BMMS Configuration:")
print(f"  BMMS Mode: {settings.BMMS_MODE}")
print(f"  Multi-tenant: {settings.RBAC_SETTINGS['ENABLE_MULTI_TENANT']}")
print(f"  Organization Switching: {settings.RBAC_SETTINGS['ALLOW_ORGANIZATION_SWITCHING']}")
print(f"  OCM Organization: {settings.RBAC_SETTINGS['OCM_ORGANIZATION_CODE']}")
EOF

# Performance check
echo "⚡ Running performance checks..."

python manage.py shell << 'EOF'
from django.db import connection
from django.core.cache import cache

# Database connection test
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user")
    user_count = cursor.fetchone()[0]
    print(f"✅ Database connection OK ({user_count} users found)")

# Cache connection test
try:
    cache.set('env_setup_test', 'ok', 60)
    cache_result = cache.get('env_setup_test')
    if cache_result == 'ok':
        print("✅ Cache connection OK")
    else:
        print("⚠️  Cache connection issue")
except Exception as e:
    print(f"⚠️  Cache connection failed: {e}")
EOF

echo ""
echo "=========================================="
echo "✅ PRODUCTION ENVIRONMENT SETUP COMPLETE"
echo "=========================================="

echo ""
echo "📋 Next Steps:"
echo "1. Review and update ../.env with your production values"
echo "2. Configure PostgreSQL for production (recommended)"
echo "3. Set up SSL certificates"
echo "4. Configure reverse proxy (Nginx/Apache)"
echo "5. Run: ./start_production.sh"
echo ""

echo "🚀 Ready for production deployment!"

# Create status file
echo "Production environment setup completed at $(date)" > setup_production_complete.txt

echo "📝 Setup complete status saved to setup_production_complete.txt"