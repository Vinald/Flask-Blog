#!/bin/bash
# Docker utility scripts for Flask Blog

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header() {
    echo ""
    echo "======================================"
    echo "$1"
    echo "======================================"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if .env exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success ".env file created"
        else
            print_error ".env.example not found!"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Start development environment
dev_start() {
    print_header "Starting Development Environment"
    check_docker
    check_env

    print_success "Building and starting containers..."
    docker-compose -f docker-compose.dev.yml up --build
}

# Start production environment
prod_start() {
    print_header "Starting Production Environment"
    check_docker
    check_env

    print_success "Building and starting containers..."
    docker-compose up --build -d

    print_success "Containers started successfully!"
    echo ""
    echo "Access the application:"
    echo "  Web:      http://localhost:5000"
    echo "  API Docs: http://localhost:5000/api/v1/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
}

# Stop all containers
stop() {
    print_header "Stopping Containers"
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_success "All containers stopped"
}

# View logs
logs() {
    print_header "Viewing Logs"
    docker-compose logs -f
}

# Run migrations
migrate() {
    print_header "Running Database Migrations"
    docker-compose exec web flask db upgrade
    print_success "Migrations applied"
}

# Create migration
create_migration() {
    if [ -z "$1" ]; then
        print_error "Please provide migration message"
        echo "Usage: ./docker.sh create-migration 'migration message'"
        exit 1
    fi

    print_header "Creating Migration"
    docker-compose exec web flask db migrate -m "$1"
    print_success "Migration created"
}

# Run tests
test() {
    print_header "Running Tests"
    docker-compose exec web python -m pytest tests/ -v
}

# Backup database
backup() {
    print_header "Backing Up Database"
    DATE=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups
    docker-compose exec -T db pg_dump -U postgres flask_blog > "backups/backup_$DATE.sql"
    print_success "Backup created: backups/backup_$DATE.sql"
}

# Restore database
restore() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file"
        echo "Usage: ./docker.sh restore backups/backup_YYYYMMDD_HHMMSS.sql"
        exit 1
    fi

    print_header "Restoring Database"
    print_warning "This will overwrite the current database!"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec -T db psql -U postgres flask_blog < "$1"
        print_success "Database restored from: $1"
    else
        print_warning "Restore cancelled"
    fi
}

# Clean everything (removes volumes)
clean() {
    print_header "Cleaning Up"
    print_warning "This will remove all containers, images, and volumes (DATA WILL BE LOST!)"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.dev.yml down -v --rmi all
        print_success "Cleanup complete"
    else
        print_warning "Cleanup cancelled"
    fi
}

# Shell into container
shell() {
    print_header "Opening Container Shell"
    docker-compose exec web /bin/bash
}

# Flask shell
flask_shell() {
    print_header "Opening Flask Shell"
    docker-compose exec web flask shell
}

# Show help
show_help() {
    cat << EOF
Flask Blog - Docker Management Script

Usage: ./docker.sh [command]

Commands:
  dev-start          Start development environment with hot reload
  prod-start         Start production environment (detached)
  stop               Stop all containers
  logs               View container logs
  migrate            Run database migrations
  create-migration   Create new migration (requires message)
  test               Run test suite in container
  backup             Backup database to backups/ directory
  restore            Restore database from backup file
  shell              Open bash shell in web container
  flask-shell        Open Flask shell for database operations
  clean              Remove all containers, images, and volumes
  help               Show this help message

Examples:
  ./docker.sh dev-start
  ./docker.sh create-migration "Add user profile field"
  ./docker.sh backup
  ./docker.sh restore backups/backup_20260301_120000.sql
  ./docker.sh test

For more information, see DOCKER.md
EOF
}

# Main script logic
case "$1" in
    dev-start)
        dev_start
        ;;
    prod-start)
        prod_start
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    migrate)
        migrate
        ;;
    create-migration)
        create_migration "$2"
        ;;
    test)
        test
        ;;
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    shell)
        shell
        ;;
    flask-shell)
        flask_shell
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
