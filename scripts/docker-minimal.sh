#!/bin/bash

# OBCMS Minimal Docker Startup Script
# Fast development setup with minimal dependencies

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
    echo -e "${PURPLE}  OBCMS Minimal Docker Setup${NC}"
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
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to setup environment
setup_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.docker.dev ]; then
            cp .env.docker.dev .env
            print_success "Created .env from development template."
        else
            print_error "No environment template found."
            exit 1
        fi
    fi
}

# Function to start minimal services
start_minimal() {
    print_header
    print_status "Starting OBCMS minimal Docker environment..."

    setup_environment

    print_status "Building minimal Docker image..."
    docker-compose -f docker-compose.minimal.yml build

    print_status "Starting services..."
    docker-compose -f docker-compose.minimal.yml up -d

    print_status "Waiting for database to be ready..."
    sleep 5

    print_status "Running database migrations..."
    docker-compose -f docker-compose.minimal.yml exec -T web python src/manage.py migrate --noinput || true

    print_status "Collecting static files..."
    docker-compose -f docker-compose.minimal.yml exec -T web python src/manage.py collectstatic --noinput || true

    print_success "OBCMS minimal environment is ready!"
    echo ""
    echo "🌐 Access the application:"
    echo "   • Web: http://localhost:8000"
    echo "   • Admin: http://localhost:8000/admin/"
    echo ""
    echo "📊 Service status:"
    docker-compose -f docker-compose.minimal.yml ps
    echo ""
    echo "📝 Useful Commands:"
    echo "   • View logs: docker-compose -f docker-compose.minimal.yml logs -f"
    echo "   • Stop services: docker-compose -f docker-compose.minimal.yml down"
    echo "   • Create superuser: docker-compose -f docker-compose.minimal.yml exec web python src/manage.py createsuperuser"
}

# Function to stop services
stop_services() {
    print_status "Stopping minimal services..."
    docker-compose -f docker-compose.minimal.yml down
    print_success "Services stopped."
}

# Function to show logs
show_logs() {
    docker-compose -f docker-compose.minimal.yml logs -f
}

# Function to open Django shell
open_shell() {
    docker-compose -f docker-compose.minimal.yml exec web python src/manage.py shell
}

# Function to create superuser
create_superuser() {
    docker-compose -f docker-compose.minimal.yml exec web python src/manage.py createsuperuser
}

# Function to show usage
show_usage() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start         Start minimal OBCMS environment (default)"
    echo "  stop          Stop services"
    echo "  logs          Show logs"
    echo "  shell         Open Django shell"
    echo "  superuser     Create Django superuser"
    echo "  help          Show this help message"
    echo ""
    echo "Minimal Setup includes:"
    echo "  • Django web application"
    echo "  • PostgreSQL database"
    echo "  • Redis cache"
    echo "  • Basic static files"
    echo ""
    echo "For full features (Celery, Flower, AI services), use:"
    echo "  ./scripts/docker-dev.sh start"
    echo ""
}

# Main script logic
main() {
    check_docker

    case "${1:-start}" in
        start)
            start_minimal
            ;;
        stop)
            stop_services
            ;;
        logs)
            show_logs
            ;;
        shell)
            open_shell
            ;;
        superuser)
            create_superuser
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"