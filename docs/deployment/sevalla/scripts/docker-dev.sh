#!/bin/bash

# OBCMS Docker Development Helper Script
# Quick commands for development workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  OBCMS Docker Dev Helper${NC}"
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

print_command() {
    echo -e "${CYAN}[CMD]${NC} $1"
}

# Function to show quick start info
show_quick_start() {
    print_header
    echo "🚀 Quick Start Commands:"
    echo ""
    print_command "./scripts/docker-dev.sh start"
    echo "  → Start all services (web, db, redis, celery, flower)"
    echo ""
    print_command "./scripts/docker-dev.sh manage createsuperuser"
    echo "  → Create admin user"
    echo ""
    print_command "./scripts/docker-dev.sh shell"
    echo "  → Open Django shell"
    echo ""
    print_command "./scripts/docker-dev.sh logs web"
    echo "  → View web service logs"
    echo ""
    echo "📱 Access URLs:"
    echo "  • Web App: http://localhost:8000"
    echo "  • Admin: http://localhost:8000/admin/"
    echo "  • Flower: http://localhost:5555"
    echo ""
    echo "🛠️  Development Commands:"
    echo "  • migrate: Run database migrations"
    echo "  • makemigrations: Create new migrations"
    echo "  • test: Run tests"
    echo "  • collectstatic: Collect static files"
    echo "  • reset: Reset database (WARNING: deletes data)"
    echo ""
}

# Function to execute docker-compose with service
execute_compose() {
    docker-compose "$@"
}

# Function to start services
start_services() {
    print_status "Starting OBCMS development environment..."
    execute_compose up -d

    print_status "Waiting for services to be ready..."
    sleep 5

    # Check if services are running
    if execute_compose ps | grep -q "Up"; then
        print_success "Services started successfully!"
        echo ""
        echo "🌐 Access the application:"
        echo "   • Web: http://localhost:8000"
        echo "   • Admin: http://localhost:8000/admin/"
        echo "   • Flower: http://localhost:5555"
        echo ""
        echo "📊 Check status: ./scripts/docker-dev.sh status"
        echo "📝 View logs: ./scripts/docker-dev.sh logs"
    else
        print_error "Some services failed to start. Check logs with 'docker-compose logs'"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    execute_compose down
    print_success "All services stopped."
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    execute_compose restart
    print_success "Services restarted."
}

# Function to show service status
show_status() {
    print_header
    echo "📊 Service Status:"
    echo ""
    execute_compose ps
    echo ""
    echo "🔗 URLs:"
    echo "   • Web: http://localhost:8000"
    echo "   • Admin: http://localhost:8000/admin/"
    echo "   • Flower: http://localhost:5555"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        print_status "Showing logs for all services..."
        execute_compose logs -f
    else
        print_status "Showing logs for service: $service"
        execute_compose logs -f "$service"
    fi
}

# Function to run Django management commands
run_manage() {
    if [ -z "$1" ]; then
        print_error "Please specify a Django management command"
        echo "Example: ./scripts/docker-dev.sh manage migrate"
        exit 1
    fi

    print_status "Running Django management command: manage $*"
    execute_compose exec web python src/manage.py "$@"
}

# Function to open shells
open_shell() {
    case "$1" in
        django|shell)
            print_status "Opening Django shell..."
            execute_compose exec web python src/manage.py shell
            ;;
        db|database)
            print_status "Opening database shell..."
            execute_compose exec db psql -U obcms -d obcms
            ;;
        redis)
            print_status "Opening Redis shell..."
            execute_compose exec redis redis-cli
            ;;
        *)
            print_error "Unknown shell type: $1"
            echo "Available shells: django, db, redis"
            exit 1
            ;;
    esac
}

# Function to run tests
run_tests() {
    print_status "Running Django tests..."
    execute_compose exec web python src/manage.py test "$@"
}

# Function to reset database
reset_database() {
    print_warning "This will RESET the database and delete all data!"
    read -p "Are you sure you want to continue? (yes/no): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Database reset cancelled"
        exit 1
    fi

    print_status "Resetting database..."
    execute_compose down -v
    execute_compose up -d db redis

    print_status "Waiting for database to be ready..."
    sleep 10

    print_status "Running migrations..."
    execute_compose exec -T web python src/manage.py migrate

    print_success "Database reset completed."
    print_status "You may want to create a superuser: ./scripts/docker-dev.sh manage createsuperuser"
}

# Function to build containers
build_containers() {
    print_status "Building Docker containers..."
    execute_compose build --no-cache
    print_success "Containers built successfully."
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    execute_compose down -v --remove-orphans
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed."
}

# Function to show usage
show_usage() {
    print_header
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "🚀 Quick Commands:"
    echo "  start           Start all development services"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  status          Show service status and URLs"
    echo "  logs [service]  Show logs (all services or specific service)"
    echo ""
    echo "🛠️  Development Commands:"
    echo "  manage <cmd>    Run Django management command"
    echo "  shell <type>    Open shell (django, db, redis)"
    echo "  test [args]     Run Django tests"
    echo "  reset           Reset database (WARNING: deletes data)"
    echo ""
    echo "🔧 Maintenance Commands:"
    echo "  build           Rebuild Docker containers"
    echo "  clean           Clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "📖 Examples:"
    echo "  $0 start                           # Start development environment"
    echo "  $0 manage createsuperuser          # Create admin user"
    echo "  $0 manage migrate                  # Run migrations"
    echo "  $0 manage makemigrations myapp     # Create migrations"
    echo "  $0 shell django                    # Open Django shell"
    echo "  $0 logs web                        # View web service logs"
    echo "  $0 test                            # Run all tests"
    echo "  $0 test myapp.tests                # Run specific tests"
    echo ""
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        manage)
            shift
            run_manage "$@"
            ;;
        shell)
            open_shell "$2"
            ;;
        test)
            shift
            run_tests "$@"
            ;;
        reset)
            reset_database
            ;;
        build)
            build_containers
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h|"")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Run main function with all arguments
main "$@"