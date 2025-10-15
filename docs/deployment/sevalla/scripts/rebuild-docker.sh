#!/bin/bash

# OBCMS Docker Rebuild Script
# This script rebuilds all Docker containers with the latest configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  OBCMS Docker Rebuild Script${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        print_status "After starting Docker, run this script again."
        exit 1
    fi
}

# Function to stop existing services
stop_services() {
    print_status "Stopping existing services..."
    docker-compose down --remove-orphans || true
    print_success "Services stopped."
}

# Function to clean up old images and containers
cleanup_old() {
    print_status "Cleaning up old Docker resources..."

    # Remove stopped containers
    docker container prune -f || true

    # Remove unused images
    docker image prune -f || true

    # Remove build cache
    docker builder prune -f || true

    print_success "Cleanup completed."
}

# Function to rebuild images without cache
rebuild_images() {
    print_status "Rebuilding Docker images (no cache)..."

    # Build development images
    print_status "Building development target..."
    docker-compose build --no-cache --pull

    # Build production target
    print_status "Building production target..."
    docker-compose build --no-cache --pull target=production

    print_success "All images rebuilt successfully."
}

# Function to rebuild specific service
rebuild_service() {
    local service=$1
    if [ -z "$service" ]; then
        print_error "Please specify a service to rebuild"
        echo "Available services: web, celery, celery-beat, flower"
        exit 1
    fi

    print_status "Rebuilding service: $service"
    docker-compose build --no-cache --pull "$service"
    print_success "Service $service rebuilt successfully."
}

# Function to rebuild production only
rebuild_production() {
    print_status "Rebuilding production environment..."

    # Stop any existing services
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true

    # Build production images
    docker-compose -f docker-compose.prod.yml build --no-cache --pull

    print_success "Production environment rebuilt."
}

# Function to rebuild with layer cache
rebuild_with_cache() {
    print_status "Rebuilding Docker images (with cache)..."
    docker-compose build --pull
    print_success "Images rebuilt with cache."
}

# Function to start services after rebuild
start_services() {
    print_status "Starting services after rebuild..."

    # Start development services
    docker-compose up -d

    print_status "Waiting for services to be ready..."
    sleep 10

    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec -T web python src/manage.py migrate --noinput || true

    # Collect static files
    print_status "Collecting static files..."
    docker-compose exec -T web python src/manage.py collectstatic --noinput || true

    print_success "Services started successfully!"

    echo ""
    echo "🌐 Access the application:"
    echo "   • Web: http://localhost:8000"
    echo "   • Admin: http://localhost:8000/admin/"
    echo "   • Flower: http://localhost:5555"
}

# Function to show rebuild options
show_usage() {
    print_header
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Rebuild Options:"
    echo "  full            Full rebuild (stop, clean, rebuild all, start)"
    echo "  images          Rebuild all images without cache"
    echo "  production      Rebuild production environment only"
    echo "  cached          Rebuild with layer cache (faster)"
    echo "  service <name>  Rebuild specific service"
    echo ""
    echo "Utility Options:"
    echo "  clean           Clean up old Docker resources only"
    echo "  stop            Stop all services only"
    echo "  start           Start services only (after rebuild)"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 full                    # Complete rebuild process"
    echo "  $0 images                  # Rebuild images only"
    echo "  $0 service web             # Rebuild web service only"
    echo "  $0 production              # Rebuild production environment"
    echo ""
}

# Main script logic
main() {
    case "${1:-full}" in
        full)
            check_docker
            print_header
            stop_services
            cleanup_old
            rebuild_images
            start_services
            ;;
        images)
            check_docker
            rebuild_images
            ;;
        production)
            check_docker
            rebuild_production
            ;;
        cached)
            check_docker
            rebuild_with_cache
            ;;
        service)
            check_docker
            rebuild_service "$2"
            ;;
        clean)
            check_docker
            cleanup_old
            ;;
        stop)
            check_docker
            stop_services
            ;;
        start)
            check_docker
            start_services
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"