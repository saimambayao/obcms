#!/bin/bash

# OBCMS Docker Startup Script
# This script helps start the OBCMS application with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs media staticfiles backups
    mkdir -p config/nginx config/redis config/postgres
    mkdir -p scripts
    print_success "Directories created successfully."
}

# Function to setup environment file
setup_environment() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.docker.dev ]; then
            cp .env.docker.dev .env
            print_success "Created .env from development template."
            print_warning "Please review and update .env file with your configuration."
        elif [ -f .env.docker ]; then
            cp .env.docker .env
            print_success "Created .env from Docker template."
            print_warning "Please review and update .env file with your configuration."
        else
            print_error "No environment template found."
            exit 1
        fi
    else
        print_status "Environment file already exists."
    fi
}

# Function to build and start services
start_services() {
    print_status "Building Docker images..."
    docker-compose build --no-cache

    print_status "Starting services..."
    docker-compose up -d

    print_status "Waiting for services to be healthy..."
    sleep 10

    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Services started successfully!"
        echo ""
        echo "=== Service URLs ==="
        echo "🌐 Web Application: http://localhost:8000"
        echo "🌸 Flower (Celery Monitoring): http://localhost:5555"
        echo "🐘 PostgreSQL: localhost:5432"
        echo "🔴 Redis: localhost:6379"
        echo ""
        echo "=== Useful Commands ==="
        echo "📊 View logs: docker-compose logs -f"
        echo "🛑 Stop services: docker-compose down"
        echo "🔄 Restart services: docker-compose restart"
        echo "📈 Check status: docker-compose ps"
    else
        print_error "Some services failed to start. Check logs with 'docker-compose logs'"
        exit 1
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec web python src/manage.py migrate --noinput
    print_success "Database migrations completed."
}

# Function to create superuser
create_superuser() {
    print_status "Creating superuser..."
    docker-compose exec web python src/manage.py createsuperuser
    print_success "Superuser created successfully."
}

# Function to load initial data
load_initial_data() {
    print_status "Loading initial data..."
    docker-compose exec web python src/manage.py loaddata fixtures/initial_data.json || true
    print_success "Initial data loaded (if fixtures exist)."
}

# Function to show usage
show_usage() {
    echo "OBCMS Docker Startup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start       Start all services (default)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs"
    echo "  status      Show service status"
    echo "  migrate     Run database migrations"
    echo "  superuser   Create Django superuser"
    echo "  shell       Open Django shell"
    echo "  db-shell    Open database shell"
    echo "  build       Rebuild Docker images"
    echo "  clean       Clean up Docker resources"
    echo "  help        Show this help message"
    echo ""
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped."
}

# Function to show logs
show_logs() {
    docker-compose logs -f
}

# Function to show status
show_status() {
    docker-compose ps
}

# Function to open Django shell
open_shell() {
    docker-compose exec web python src/manage.py shell
}

# Function to open database shell
open_db_shell() {
    docker-compose exec db psql -U obcms -d obcms
}

# Function to rebuild images
rebuild_images() {
    print_status "Rebuilding Docker images..."
    docker-compose build --no-cache
    print_success "Docker images rebuilt."
}

# Function to clean up
clean_up() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Docker cleanup completed."
}

# Main script logic
main() {
    check_docker
    check_docker_compose

    case "${1:-start}" in
        start)
            create_directories
            setup_environment
            start_services
            run_migrations
            load_initial_data
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        migrate)
            run_migrations
            ;;
        superuser)
            create_superuser
            ;;
        shell)
            open_shell
            ;;
        db-shell)
            open_db_shell
            ;;
        build)
            rebuild_images
            ;;
        clean)
            clean_up
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
