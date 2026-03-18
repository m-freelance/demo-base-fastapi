### Build dependencies ###
# the stage is used to compile dependencies and create a virtual environment
# this allows us to keep the final image small and only include runtime dependencies
FROM python:3.14-slim AS builder

WORKDIR /backend

# install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# install pip-tools for dependency compilation
RUN pip install --no-cache-dir pip-tools

# copy dependency files
COPY requirements.in .
COPY requirements-dev.in .

# compile dependencies
RUN pip-compile requirements.in -o requirements.txt --strip-extras
RUN pip-compile requirements-dev.in -o requirements-dev.txt --strip-extras

# install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

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

# copy compiled dev requirements from builder
COPY --from=builder /backend/requirements-dev.txt .

# install development dependencies
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements-dev.txt

USER appuser

# override CMD for development with hot reload
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

