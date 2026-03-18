# Demo Base FastAPI

A production-ready FastAPI application template with authentication, user management, and database integration.

![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [License](#-license)

## ✨ Features

- **🔐 Authentication** - JWT-based authentication with secure password hashing (Argon2)
- **👤 User Management** - User registration, login, and profile management
- **📄 Pagination** - Built-in pagination support with fastapi-pagination
- **🗃️ Database** - Async PostgreSQL with SQLAlchemy 2.0 and Alembic migrations
- **🐳 Docker Ready** - Multi-stage Docker builds for development and production
- **⚙️ Configuration** - YAML-based configuration with environment overrides
- **🧪 Testing** - Comprehensive test suite with pytest
- **📝 API Docs** - Interactive OpenAPI (Swagger) documentation

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL 17 + SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Authentication | JWT (PyJWT) + Argon2 |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Containerization | Docker + Docker Compose |

## 📁 Project Structure

```
demo-base-fastapi/
├── backend/
│   ├── api/
│   │   ├── alembic/          # Database migrations
│   │   ├── auth/             # Authentication module
│   │   ├── config/           # Configuration management
│   │   ├── db/               # Database client and dependencies
│   │   ├── middleware/       # Custom middleware (auth, error handling)
│   │   ├── schemas/          # SQLAlchemy models
│   │   ├── user/             # User management module
│   │   ├── utils/            # Utility functions
│   │   ├── main.py           # Application factory
│   │   └── router.py         # API router configuration
│   ├── resources/            # Configuration files
│   │   ├── default_config.yaml
│   │   ├── local_config.yaml
│   │   ├── prod_config.yaml
│   │   └── test_config.yaml
│   ├── tests/                # Test suite
│   ├── Dockerfile
│   ├── requirements.in
│   └── pyproject.toml
├── docs/
│   └── screenshots/          # OpenAPI screenshots
├── compose.yml
├── Makefile
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.14+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 17 (for local development without Docker)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd demo-base-fastapi
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the application**
   ```bash
   # Production mode
   make up

   # Development mode (with hot reload)
   make up-dev
   ```

4. **Run database migrations**
   ```bash
   make migrate
   # or for dev
   make migrate-dev
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development (without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   # For development
   pip install -r backend/requirements-dev.txt
   ```

3. **Configure environment**
   ```bash
   export DEPLOYMENT_TYPE=local
   export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   export JWT_SECRET_KEY=your-secret-key
   ```

4. **Run the application**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

## 📖 API Documentation

The API provides interactive documentation at:

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative documentation view
- **OpenAPI JSON**: `/openapi.json` - Raw OpenAPI specification

### API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Health check | ❌ |
| `POST` | `/api/v1/auth/register` | Register new user | ❌ |
| `POST` | `/api/v1/auth/login` | User login | ❌ |
| `GET` | `/api/v1/users/me` | Get current user | ✅ |
| `GET` | `/api/v1/users` | List all users | ✅ |

### Screenshots

<details>
<summary>📸 Click to expand OpenAPI Screenshots</summary>

#### Swagger UI Overview
![Swagger UI Overview](docs/images/swagger-overview.png)

#### Authentication Endpoints
![Auth Endpoints](docs/images/auth-endpoint.png)

#### User Endpoints
![User Endpoints](docs/images/user-endpoint.png)

#### Example Request/Response
![Example Request](docs/images/example-request.png)

</details>

> **📝 Note:** To add screenshots, save your images to the `docs/screenshots/` folder with the following names:
> - `swagger-overview.png` - Main Swagger UI page
> - `auth-endpoints.png` - Authentication endpoints section
> - `user-endpoints.png` - User management endpoints section
> - `example-request.png` - Example of a request/response

## 💻 Development

### Available Make Commands

```bash
make help              # Show all available commands

# Docker commands
make build             # Build production Docker image
make build-dev         # Build development Docker image
make up                # Start production services
make up-dev            # Start development services with hot reload
make down              # Stop all services
make logs              # View logs from all services
make shell             # Open shell in backend container
make clean             # Remove containers, images, and volumes

# Database
make migrate           # Run database migrations
make migrate-dev       # Run migrations in dev environment

# Dependencies
make compile-deps      # Compile requirements.in to requirements.txt
```

### Dependency Management

This project uses `pip-tools` for dependency management:

```bash
# Install pip-tools
pip install pip-tools

# Compile dependencies
make compile-deps
```

## 🧪 Testing

### Run Tests in Docker

```bash
make test              # Run all tests
make test-unit         # Run only unit tests
make test-release      # Run only release tests
make test-fast         # Run tests excluding release tests
```

### Run Tests Locally

```bash
make test-local        # Run all tests locally
make test-local-unit   # Run only unit tests (fast, no database)
make test-local-release # Run only release tests (with database)
make test-local-fast   # Run tests excluding release tests
```

### Test Markers

| Marker | Description |
|--------|-------------|
| `unit` | Fast unit tests, no external dependencies |
| `integration` | Integration tests |
| `release` | Release tests requiring full setup |

## ⚙️ Configuration

Configuration is managed through YAML files in `backend/resources/`:

| File | Purpose |
|------|---------|
| `default_config.yaml` | Base configuration |
| `local_config.yaml` | Local development settings |
| `prod_config.yaml` | Production settings |
| `test_config.yaml` | Test environment settings |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEPLOYMENT_TYPE` | Environment type (local/prod/test) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `CONFIG_PATHS` | Config file paths (semicolon-separated) | No |

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ using FastAPI
</p>

