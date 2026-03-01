# Flask Blog - Makefile for common tasks
.PHONY: help install dev prod stop clean test migrate backup shell

# Default target
help:
	@echo "Flask Blog - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install      - Install dependencies locally"
	@echo "  make dev          - Run development server locally"
	@echo "  make dev-docker   - Run development server in Docker"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production server in Docker"
	@echo "  make prod-local   - Run production server locally with gunicorn"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migration    - Create new migration (use MSG='description')"
	@echo "  make db-reset     - Reset database (WARNING: deletes data)"
	@echo "  make backup       - Backup database"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-api     - Run API tests only"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make test-docker  - Run tests in Docker"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make docker-shell - Open shell in container"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean up cache files"
	@echo "  make lint         - Run code linters"
	@echo "  make format       - Format code"
	@echo "  make shell        - Open Flask shell"
	@echo ""

# Local development
install:
	pip install -r requirements.txt

dev:
	flask run --debug

dev-docker:
	docker-compose -f docker-compose.dev.yml up

# Production
prod:
	docker-compose up --build -d

prod-local:
	gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app

# Database
migrate:
	flask db upgrade

migration:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide MSG='migration message'"; \
		exit 1; \
	fi
	flask db migrate -m "$(MSG)"

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Continue? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	flask db downgrade base
	flask db upgrade

backup:
	@mkdir -p backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	if [ -n "$$(docker-compose ps -q db)" ]; then \
		docker-compose exec -T db pg_dump -U postgres flask_blog > "backups/backup_$$DATE.sql"; \
		echo "Backup created: backups/backup_$$DATE.sql"; \
	else \
		echo "Database not running. Start with 'make prod' first."; \
	fi

# Testing
test:
	python -m pytest tests/ -v

test-api:
	python -m pytest tests/test_api.py -v

test-cov:
	python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-docker:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from test

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec web /bin/bash

# Utilities
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .pytest_cache/ .coverage
	@echo "✓ Cleaned cache files"

lint:
	@echo "Running linters..."
	@which flake8 > /dev/null && flake8 app/ || echo "Install flake8: pip install flake8"

format:
	@echo "Formatting code..."
	@which black > /dev/null && black app/ tests/ || echo "Install black: pip install black"

shell:
	flask shell

stop:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Install and setup
setup: install
	@echo "Creating .env file..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "Running migrations..."
	@flask db upgrade || true
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your settings"
	@echo "  2. Run 'make dev' to start development server"
	@echo "  3. Visit http://localhost:5000"
