# Makefile for demo-base-fastapi

.PHONY: help build build-dev up up-dev down logs shell test test-local test-unit test-fast test-release test-local-unit test-local-fast test-local-release clean compile-deps

# Default target
help:
	@echo "Available targets:"
	@echo "  build        - Build production Docker image"
	@echo "  build-dev    - Build development Docker image"
	@echo "  up           - Start production services"
	@echo "  up-dev       - Start development services with hot reload"
	@echo "  down         - Stop all services"
	@echo "  logs         - View logs from all services"
	@echo "  shell        - Open shell in backend container"
	@echo "  test         - Run tests in container"
	@echo "  test-unit    - Run only unit tests in container"
	@echo "  test-release - Run only release tests in container"
	@echo "  test-fast  - Run tests excluding release tests in container"
	@echo "  test-local   - Run all tests locally"
	@echo "  test-local-unit    - Run only unit tests (fast, no database)"
	@echo "  test-local-release - Run only release tests (with database)"
	@echo "  test-local-fast    - Run tests excluding release tests"
	@echo "  clean        - Remove containers, images, and volumes"
	@echo "  compile-deps - Compile requirements.in to requirements.txt"
	@echo "  migrate      - Run database migrations"

### Docker related targets ###
# Build production image
build:
	docker compose build backend

# Build development image
build-dev:
	docker compose --profile dev build backend-dev

# Start production services
up:
	docker compose up -d database backend

# Start development services
up-dev:
	docker compose --profile dev up -d database backend-dev

# Stop all services
down:
	docker compose --profile dev down

# View logs
logs:
	docker compose logs -f

# Open shell in backend container
shell:
	docker compose exec backend /bin/bash


# Run tests
test:
	docker compose --profile dev run --rm backend-dev pytest


# Run unit tests
test-unit:
	docker compose --profile dev run --rm backend-dev pytest -m "unit"


# Run release tests
test-release:
	docker compose --profile dev run --rm backend-dev pytest -m "release"


# Run tests excluding release tests
test-fast:
	docker compose --profile dev run --rm backend-dev pytest -m "not release"


# Clean up
clean:
	docker compose --profile dev down -v --rmi local
	docker system prune -f


# Run database migrations
migrate:
	docker compose exec backend alembic upgrade head

# Run migrations in dev
migrate-dev:
	docker compose exec backend-dev alembic upgrade head

### Local development targets ###
# Compile dependencies
compile-deps:
	cd backend && pip-compile requirements.in -o requirements.txt --strip-extras
	cd backend && pip-compile requirements-dev.in -o requirements-dev.txt --strip-extras

# Run all tests locally
test-local:
	cd backend && PYTHONPATH=.. python -m pytest tests -v

# Run only unit tests (fast, no database)
test-local-unit:
	cd backend && PYTHONPATH=.. python -m pytest tests -m "unit" -v

# Run only release tests (with database)
test-local-release:
	cd backend && PYTHONPATH=.. python -m pytest tests -m "release" -v

# Run tests excluding release tests (for CI fast feedback)
test-local-fast:
	cd backend && PYTHONPATH=.. python -m pytest tests -m "not release" -v
