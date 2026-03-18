# Docker Build Guide

This document explains how to build and run the demo-base-fastapi application using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

## Quick Start

### 1. Set up environment variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 2. Build and run (Production)

```bash
# Build the backend image
docker compose build backend

# Start all services
docker compose up -d
```

### 3. Build and run (Development with hot reload)

```bash
# Start development environment
docker compose --profile dev up -d backend-dev
```

## Using the Makefile

For convenience, you can use the provided Makefile:

```bash
# Show available commands
make help

# Build production image
make build

# Start production services
make up

# Start development services
make up-dev

# View logs
make logs

# Stop services
make down

# Run tests
make test

# Clean up
make clean
```

## Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `database` | PostgreSQL 17.0 database | 5432 |
| `backend` | Production FastAPI application | 8000 |
| `backend-dev` | Development FastAPI with hot reload | 8000 |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | postgres |
| `POSTGRES_PASSWORD` | Database password | postgres |
| `POSTGRES_DB` | Database name | postgres |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | (required) |
| `DEPLOYMENT_TYPE` | Deployment environment | local |

## Dependency Management

This project uses `pip-tools` for dependency management:

### Files

- `requirements.in` - Base production dependencies
- `requirements-dev.in` - Development dependencies (includes base)
- `requirements.txt` - Compiled production dependencies (auto-generated)
- `requirements-dev.txt` - Compiled dev dependencies (auto-generated)

### Compile dependencies locally

```bash
# Install pip-tools
pip install pip-tools

# Compile requirements
make compile-deps

# Or manually:
cd backend
pip-compile requirements.in -o requirements.txt --strip-extras
pip-compile requirements-dev.in -o requirements-dev.txt --strip-extras
```

## Health Checks

The API includes a health check endpoint at `/health` that returns:

```json
{"status": "healthy"}
```

This is used by Docker for container health monitoring.

## Database Migrations

Run Alembic migrations:

```bash
# Production
make migrate

# Development
make migrate-dev
```

## Troubleshooting

### Container won't start

1. Check logs: `docker compose logs backend`
2. Verify environment variables in `.env`
3. Ensure database is healthy: `docker compose ps`

### Database connection issues

1. Wait for database health check to pass
2. Verify `DATABASE_URL` is correctly set
3. Check network connectivity: `docker compose exec backend ping database`

