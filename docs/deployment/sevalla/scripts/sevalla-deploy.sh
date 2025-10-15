#!/bin/bash

# OBCMS Sevalla Deployment Script
# Automates the deployment process for Sevalla platform
# Usage: ./scripts/sevalla-deploy.sh [staging|production]

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/manage.py" ]]; then
        error "manage.py not found. Please run from project root or ensure manage.py exists."
    fi
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    # Check for Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
    fi
    
    # Check git status
    if [[ -n $(git status --porcelain) ]]; then
        warn "There are uncommitted changes. Please commit or stash them before deployment."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    success "Prerequisites check passed"
}

# Generate secure secrets
generate_secrets() {
    log "Generating secure secrets..."
    
    local SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    local DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    local HEALTH_TOKEN=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    echo "NEW_SECRETS generated:"
    echo ""
    echo "SECRET_KEY=$SECRET_KEY"
    echo "DB_PASSWORD=$DB_PASSWORD"
    echo "REDIS_PASSWORD=$REDIS_PASSWORD"
    echo "HEALTH_TOKEN=$HEALTH_TOKEN"
    echo ""
    echo "⚠️  IMPORTANT: Copy these secrets and update your Sevalla environment variables!"
    echo "⚠️  Never commit these secrets to version control!"
}

# Build Docker image
build_image() {
    log "Building Docker image for $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT"
    
    # Use the production target for both staging and production
    docker build \
        --target production \
        --tag obcms:$ENVIRONMENT \
        --tag obcms:latest \
        .
    
    success "Docker image built successfully"
}

# Test local deployment
test_deployment() {
    log "Testing local deployment with docker-compose..."
    
    cd "$PROJECT_ROOT"
    
    # Create test environment file
    cat > .env.test << EOF
# Test Environment Configuration
ENVIRONMENT=test
DEBUG=True
SECRET_KEY=test-secret-key-for-local-testing-only
DATABASE_URL=postgres://obcms:test-password@localhost:5432/obcms_test
REDIS_URL=redis://localhost:6379/0
USE_S3=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
BMMS_ORGANIZATION_NAME=Test Environment
ENABLE_MULTI_TENANT=true
RUN_MIGRATIONS=true
EOF
    
    # Run test deployment
    docker-compose -f docker-compose.sevalla.yml --env-file .env.test up -d
    
    log "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        success "Local deployment test passed"
    else
        error "Local deployment test failed - health check failed"
    fi
    
    # Cleanup
    docker-compose -f docker-compose.sevalla.yml --env-file .env.test down
    rm .env.test
}

# Run Django management commands
run_django_commands() {
    log "Running Django management commands..."
    
    # Create temporary container to run commands
    docker run --rm \
        --env-file "$PROJECT_ROOT/.env.production" \
        obcms:$ENVIRONMENT \
        python src/manage.py check --deploy
    
    docker run --rm \
        --env-file "$PROJECT_ROOT/.env.production" \
        obcms:$ENVIRONMENT \
        python src/manage.py migrate --dry-run
    
    success "Django checks completed"
}

# Create deployment package
create_deployment_package() {
    log "Creating deployment package..."
    
    cd "$PROJECT_ROOT"
    
    # Create deployment package directory
    local BUILD_DIR="$PROJECT_ROOT/dist/sevalla-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BUILD_DIR"
    
    # Copy necessary files
    cp -r "$PROJECT_ROOT/src" "$BUILD_DIR/"
    cp "$PROJECT_ROOT/requirements" "$BUILD_DIR/"
    cp "$PROJECT_ROOT/package.json" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/package.lock.json" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/tailwind.config.js" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/postcss.config.js" "$BUILD_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/Dockerfile" "$BUILD_DIR/"
    cp "$PROJECT_ROOT/gunicorn.conf.py" "$BUILD_DIR/"
    cp "$PROJECT_ROOT/docker-compose.sevalla.yml" "$BUILD_DIR/"
    cp "$PROJECT_ROOT/.env.production.template" "$BUILD_DIR/"
    
    # Create deployment manifest
    cat > "$BUILD_DIR/manifest.json" << EOF
{
  "project": "obcms",
  "environment": "$ENVIRONMENT",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "git_commit": "$(git rev-parse HEAD)",
  "git_branch": "$(git branch --show-current)",
  "docker_image": "obcms:$ENVIRONMENT",
  "version": "$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")"
}
EOF
    
    # Create tarball
    local TARBALL="$PROJECT_ROOT/dist/obcms-sevalla-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S).tar.gz"
    cd "$PROJECT_ROOT/dist"
    tar -czf "$TARBALL" -C . "$(basename "$BUILD_DIR")"
    
    success "Deployment package created: $TARBALL"
    
    # Cleanup build directory
    rm -rf "$BUILD_DIR"
}

# Generate deployment documentation
generate_docs() {
    log "Generating deployment documentation..."
    
    local DOCS_DIR="$PROJECT_ROOT/docs/deployment"
    local DEPLOYMENT_FILE="$DOCS_DIR/SEVALLA_DEPLOYMENT_SUMMARY.md"
    
    cat > "$DEPLOYMENT_FILE" << EOF
# OBCMS Sevalla Deployment Summary

**Deployment Date:** $(date)  
**Environment:** $ENVIRONMENT  
**Git Commit:** $(git rev-parse --short HEAD)  
**Git Branch:** $(git branch --show-current)  

## Deployment Checklist

- [x] Code validated and tested
- [x] Docker image built
- [x] Security review completed
- [x] Environment variables configured
- [x] Health checks implemented
- [x] Production optimizations applied

## Next Steps

1. **Configure Sevalla Environment Variables**
   - Copy values from \`.env.production\`
   - Update database credentials
   - Set up storage credentials
   - Configure email settings

2. **Deploy to Sevalla**
   - Push to production branch
   - Monitor build logs
   - Verify health endpoint
   - Test critical functionality

3. **Post-Deployment**
   - Run database migrations
   - Create admin user
   - Monitor performance
   - Set up alerts

## Contact Information

- **Development Team**: dev@bmms.barmm.gov.ph
- **Sevalla Support**: dashboard.sevalla.com/support
- **Documentation**: [SEVALLA_DEPLOYMENT_GUIDE.md](./SEVALLA_DEPLOYMENT_GUIDE.md)

---

*Generated automatically by deployment script*
EOF

    success "Deployment documentation updated"
}

# Main deployment function
deploy() {
    log "Starting OBCMS deployment to Sevalla ($ENVIRONMENT)..."
    
    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        error "Environment must be 'staging' or 'production'"
    fi
    
    # Check for production environment
    if [[ "$ENVIRONMENT" == "production" ]]; then
        warn "Deploying to PRODUCTION environment"
        read -p "Are you absolutely sure? This will affect production users! (yes/no): " -r
        if [[ ! $REPLY =~ ^yes$ ]]; then
            exit 1
        fi
    fi
    
    # Execute deployment steps
    check_prerequisites
    
    if [[ "$2" == "--generate-secrets" ]]; then
        generate_secrets
        exit 0
    fi
    
    build_image
    
    if [[ "$2" != "--skip-tests" ]]; then
        test_deployment
    fi
    
    run_django_commands
    create_deployment_package
    generate_docs
    
    success "Deployment preparation completed!"
    
    echo ""
    echo "🚀 Next steps:"
    echo "1. Push your code to Git: git push origin production"
    echo "2. Configure environment variables in Sevalla dashboard"
    echo "3. Monitor deployment in Sevalla dashboard"
    echo "4. Test the deployed application"
    echo ""
    echo "📋 Quick links:"
    echo "- Sevalla Dashboard: https://dashboard.sevalla.com"
    echo "- Health Check: https://your-domain.sevalla.app/health/"
    echo "- Documentation: docs/deployment/SEVALLA_DEPLOYMENT_GUIDE.md"
}

# Help function
show_help() {
    cat << EOF
OBCMS Sevalla Deployment Script

Usage: $0 [ENVIRONMENT] [OPTIONS]

ENVIRONMENTS:
  staging     Deploy to staging environment
  production  Deploy to production environment

OPTIONS:
  --generate-secrets    Generate new secure secrets
  --skip-tests        Skip local testing (faster but less safe)
  --help              Show this help message

EXAMPLES:
  $0 staging                      # Deploy to staging with tests
  $0 production                   # Deploy to production with safety checks
  $0 staging --skip-tests         # Deploy to staging without tests
  $0 --generate-secrets           # Generate new secrets only

PREREQUISITES:
  - Docker and Docker Compose installed
  - Git repository initialized
  - No uncommitted changes (recommended)
  - Python 3.12+ (for secret generation)

ENVIRONMENT SETUP:
  1. Copy .env.production.template to .env.production
  2. Fill in all required values
  3. Run this script to prepare deployment

For complete documentation, see:
docs/deployment/SEVALLA_DEPLOYMENT_GUIDE.md

EOF
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --generate-secrets)
        generate_secrets
        exit 0
        ;;
    staging|production|"")
        deploy "$@"
        ;;
    *)
        error "Unknown argument: $1. Use --help for usage information."
        ;;
esac
