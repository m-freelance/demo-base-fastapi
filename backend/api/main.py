from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from backend.api.auth.token_service import TokenService
from backend.api.config.config_dependencies import get_config_service
from backend.api.config.config_service import ConfigService
from backend.api.db import AsyncDBClient

from backend.api.middleware import ErrorMiddleware, AuthMiddleware
from backend.api.router import api_router, health_router
from backend.api.utils.get_logger import get_logger

_TITLE = "Demo Base FastAPI"

_DESCRIPTION = """
## 🚀 Production-Ready FastAPI Template

A modern, async FastAPI application with authentication, user management, and PostgreSQL integration.

### Features

- **🔐 JWT Authentication** - Secure token-based authentication with Argon2 password hashing
- **👤 User Management** - Registration, login, and user profile endpoints
- **📄 Pagination** - Built-in pagination for list endpoints
- **🗃️ Async Database** - PostgreSQL with SQLAlchemy 2.0 async support
- **⚙️ Configuration** - YAML-based configuration with environment overrides

### Authentication

Protected endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

Obtain a token by calling the `/api/v1/auth/login` endpoint.
"""

_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_service: ConfigService = get_config_service()

    database_config = config_service.config.api.database
    jwt_config = config_service.config.api.jwt

    app.state.db = AsyncDBClient.from_url(
        url=database_config.url,
        echo=database_config.echo,
        pool_size=database_config.pool_size,
        max_overflow=database_config.max_overflow,
        pool_pre_ping=database_config.pool_pre_ping,
    )

    app.state.token_service = TokenService(jwt_config=jwt_config)

    yield

    await app.state.db.engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config_service: ConfigService = get_config_service()
    api_config = config_service.config.api

    app = FastAPI(
        title=_TITLE,
        description=_DESCRIPTION,
        version=_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.origins,
        allow_credentials=api_config.allow_credentials,
        allow_methods=api_config.allow_methods,
        allow_headers=["*"],
    )

    app.add_middleware(ErrorMiddleware, config=api_config.middleware.error_middleware)  # type: ignore[arg-type]
    app.add_middleware(
        AuthMiddleware,  # type: ignore[arg-type]
        config=api_config.middleware.auth_middleware,
        jwt_config=api_config.jwt,
    )
    add_pagination(app)

    app.include_router(health_router)
    app.include_router(api_router)

    return app


def run_api():
    """Run the API server with uvicorn (for direct execution)."""
    config_service: ConfigService = get_config_service()
    api_config = config_service.config.api
    logger = get_logger(__name__)
    logger.info("Starting API server...")

    app = create_app()
    uvicorn.run(app, host=api_config.host, port=api_config.port, log_level="debug")

    return app


# ASGI application instance for uvicorn to import
app = create_app()


if __name__ == "__main__":
    run_api()
