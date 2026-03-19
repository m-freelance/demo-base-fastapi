from enum import Enum

from pydantic import BaseModel

from backend.api.schemas import UserRole


class Base(BaseModel): ...


### ENUMS ###
class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ApplicationConfig(Base):
    api: ApiConfig
    logging: LoggingConfig


### Root configs ###
class ApiConfig(Base):
    title: str
    host: str
    port: int
    origins: list[str]
    allow_credentials: bool
    allow_methods: list[HttpMethod]
    database: DatabaseConfig
    middleware: MiddlewareConfig
    jwt: JWTConfig


class LoggingConfig(Base):
    level: LoggingLevel
    format: str
    date_format: str
    file: LoggingFileConfig
    handlers: list[LoggingHandlerType]


### Logging ###
class LoggingFileConfig(Base):
    enabled: bool
    max_bytes: int
    backup_count: int
    filename: str


class LoggingHandlerType(str, Enum):
    CONSOLE = "console"
    FILE = "file"


class LoggingLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


### DB ###
class DatabaseConfig(Base):
    url: str
    pool_size: int
    max_overflow: int
    pool_pre_ping: bool
    echo: bool


### Middleware ###
class MiddlewareConfig(Base):
    error_middleware: ErrorMiddlewareConfig
    auth_middleware: AuthMiddlewareConfig


class ErrorMiddlewareConfig(Base):
    return_detailed_internal_errors: bool


class AuthMiddlewareConfig(Base):
    path_access: list[PathAccessConfig]


class PathAccessConfig(Base):
    path: str
    allowed_roles: list[UserRole]
    methods: list[HttpMethod]


### JWT ###
class JWTConfig(Base):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
