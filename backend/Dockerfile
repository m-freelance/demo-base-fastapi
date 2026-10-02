### Build dependencies ###
# the stage is used to resolve dependencies and create a virtual environment
# this allows us to keep the final image small and only include runtime dependencies
FROM python:3.14-slim AS builder

# uv ships its own image, so the build never needs pip
COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /bin/uv

WORKDIR /backend

# install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# the environment sits outside the workdir so a bind mount cannot shadow it
# UV_PYTHON_DOWNLOADS=never keeps uv on the interpreter from the base image
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=/usr/local/bin/python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# copy dependency files
COPY pyproject.toml uv.lock ./

# install production dependencies from the lockfile
RUN uv sync --frozen --no-dev

### Add the dev dependency group on top of the production environment ###
FROM builder AS builder-dev

RUN uv sync --frozen

### Build the final production image ###
FROM python:3.14-slim AS production

WORKDIR /backend

# install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# copy application code
COPY --chown=appuser:appgroup . .

# create data directories
RUN mkdir -p /data/logs && chown -R appuser:appgroup /data/logs

# switch to non-root user
USER appuser

# expose the API port
EXPOSE 8000

# set environment variables for Python
# PYTHONDONTWRITEBYTECODE prevents Python from writing .pyc files, which can save space in the container
# PYTHONUNBUFFERED ensures that logs are output immediately without buffering
# PYTHONPATH is set to / to allow imports from the root of the project
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/

# health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# run the application
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


### Build the development image with hot reload ###
# the development stage is based on the production image but includes additional dependencies for development
# and overrides the CMD to enable hot reload with uvicorn
FROM production AS development

USER root

# swap in the environment that also carries the dev dependency group
COPY --from=builder-dev --chown=appuser:appgroup /opt/venv /opt/venv

USER appuser

# override CMD for development with hot reload
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

