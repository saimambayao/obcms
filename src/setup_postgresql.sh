#!/bin/bash
# PostgreSQL Setup Script for OBCMS/BMMS
# This script sets up PostgreSQL for local development and testing

set -e

echo "🗄️  PostgreSQL Setup for OBCMS/BMMS"
echo "===================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo ""
    echo "Installation options:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "  Windows: Download from https://www.postgresql.org/download/windows/"
    echo ""
    exit 1
fi

echo "✅ PostgreSQL is installed"

# Check if PostgreSQL service is running
if ! pg_isready -q &> /dev/null; then
    echo "⚠️  PostgreSQL is not running. Starting PostgreSQL..."

    # Try different methods to start PostgreSQL
    if command -v brew &> /dev/null && brew services list | grep -q postgresql; then
        echo "Starting PostgreSQL via Homebrew..."
        brew services start postgresql
    elif command -v pg_ctl &> /dev/null; then
        echo "Starting PostgreSQL via pg_ctl..."
        pg_ctl -D /usr/local/var/postgres start -l /usr/local/var/log/postgres.log
    elif command -v systemctl &> /dev/null; then
        echo "Starting PostgreSQL via systemctl..."
        sudo systemctl start postgresql
    else
        echo "❌ Could not start PostgreSQL automatically."
        echo "Please start PostgreSQL manually and try again."
        exit 1
    fi

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if pg_isready -q; then
            echo "✅ PostgreSQL is ready"
            break
        fi
        echo "   Waiting... ($i/30)"
        sleep 1
    done

    if ! pg_isready -q; then
        echo "❌ PostgreSQL failed to start properly."
        exit 1
    fi
else
    echo "✅ PostgreSQL is already running"
fi

# Check if PostgreSQL user exists
if ! psql -lqt postgres; then
    echo "⚠️  PostgreSQL user 'postgres' not found. Creating user..."

    # Try to create postgres user
    if command -v createuser &> /dev/null; then
        createuser -s postgres
    else
        echo "❌ Could not create PostgreSQL user automatically."
        echo "Please create the 'postgres' user manually:"
        echo "  sudo -u postgres createuser -s postgres"
        exit 1
    fi
else
    echo "✅ PostgreSQL user 'postgres' exists"
fi

# Database configuration
DB_NAME="obcms_prod"
DB_USER="obcms_user"
DB_PASSWORD="obcms_password"

echo "📊 Setting up OBCMS database..."

# Create database
if psql -lqt | grep -q "$DB_NAME"; then
    echo "✅ Database '$DB_NAME' already exists"
else
    echo "Creating database '$DB_NAME'..."
    createdb "$DB_NAME"
    echo "✅ Database '$DB_NAME' created"
fi

# Create user
if psql -lqt | grep -q "$DB_USER"; then
    echo "✅ User '$DB_USER' already exists"
else
    echo "Creating user '$DB_USER'..."
    createuser "$DB_USER"
    echo "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" | psql -d postgres
    echo "✅ User '$DB_USER' created"
fi

# Grant privileges
echo "Granting privileges..."
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
echo "✅ Privileges granted"

# Test connection
echo "Testing database connection..."
if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo "Please check your PostgreSQL configuration"
    exit 1
fi

# Create connection string
echo ""
echo "🔗 Database Connection String:"
echo "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

# Update .env file
if [ -f "../.env" ]; then
    echo "📝 Updating .env file with PostgreSQL configuration..."

    # Create backup
    cp ../.env ../.env.backup

    # Update DATABASE_URL in .env
    if grep -q "DATABASE_URL=sqlite://" ../.env; then
        sed -i.bak "s|DATABASE_URL=sqlite://.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|g" ../.env
        echo "✅ Updated DATABASE_URL in .env"
    else
        echo "⚠️  DATABASE_URL not found in .env. Please update it manually:"
        echo "   DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
    fi

    # Add PostgreSQL configuration if not present
    if ! grep -q "POSTGRES_DB=" ../.env; then
        echo "" >> ../.env
        echo "# PostgreSQL Configuration" >> ../.env
        echo "POSTGRES_DB=$DB_NAME" >> ../.env
        echo "POSTGRES_USER=$DB_USER" >> ../.env
        echo "POSTGRES_PASSWORD=$DB_PASSWORD" >> ../env
        echo "POSTGRES_HOST=localhost" >> ../.env
        echo "POSTGRES_PORT=5432" >> ../.env
        echo "✅ Added PostgreSQL configuration to .env"
    fi
else
    echo "⚠️  .env file not found. Please create it with:"
    echo "   cp ../.env.example ../.env"
    echo "   Then update DATABASE_URL manually"
fi

# Install psycopg2-binary
echo "📦 Installing PostgreSQL adapter..."
source ../venv/bin/activate 2>/dev/null || {
    echo "⚠️  Virtual environment not activated. Installing psycopg2-binary system-wide..."
    pip3 install psycopg2-binary
}

pip install psycopg2-binary 2>/dev/null || echo "⚠️  Could not install psycopg2-binary. Please install manually: pip install psycopg2-binary"

echo ""
echo "===================================="
echo "✅ POSTGRESQL SETUP COMPLETE"
echo "===================================="
echo ""
echo "Database Name: $DB_NAME"
echo "Database User: $DB_USER"
echo "Database Host: localhost"
echo "Database Port: 5432"
echo ""
echo "🚀 Ready for production deployment!"
echo ""
echo "Next steps:"
echo "1. Test the migration: python migrate_to_postgresql.py --export-only"
echo "2. Update production settings in .env"
echo "3. Run full migration: python migrate_to_postgresql.py"
echo "4. Test Django with PostgreSQL: python manage.py check --deploy"
echo ""

# Create status file
echo "PostgreSQL setup completed at $(date)" > postgres_setup_complete.txt

echo "📝 Setup complete status saved to postgres_setup_complete.txt"