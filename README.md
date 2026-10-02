# FastAPI + Angular Starter

User accounts, roles and an admin panel on FastAPI, PostgreSQL and Angular 21,
packaged with Docker and checked in CI.

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green.svg)
![Angular](https://img.shields.io/badge/Angular-21-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## Features

- **Accounts.** Registration and login, Argon2 password hashing, JWT access tokens that
  must carry an expiry.
- **Roles.** `user` and `admin`. Access is checked by backend middleware on every request,
  and Angular route guards mirror the same rules in the UI.
- **Access rules in config.** Protected paths, methods and allowed roles are one YAML
  block (see [Design notes](#design-notes)).
- **Admin panel.** Paginated user list, available to admins only.
- **Errors.** One JSON error shape for every failure. Stack traces are shown in local
  config and hidden in production config.
- **Database.** PostgreSQL 17 through async SQLAlchemy 2.0, schema changes through Alembic.
- **Theming.** Colors and spacing come from a single token file in the frontend design system.
- **Tests and CI.** 178 backend tests, about 200 frontend tests. Pull requests that touch
  the backend run Black, isort and mypy, then the backend test suite.
- **Containers.** Multi-stage Docker images, Docker Compose for the full stack,
  dependencies locked with uv and npm.

## Screenshots

| Login | Registration |
|-------|--------------|
| ![Login view](docs/images/frontend-login.png) | ![Registration view after a successful sign-up](docs/images/frontend-register.png) |

| Home | Profile |
|------|---------|
| ![Home view](docs/images/frontend-home.png) | ![Profile view showing the role badge](docs/images/frontend-profile.png) |

**User management (admin only)**

![Admin view with the paginated user table](docs/images/frontend-admin.png)

<details>
<summary>API documentation (Swagger UI)</summary>

![Swagger UI overview](docs/images/swagger-overview.png)
![Auth endpoints](docs/images/auth-endpoint.png)
![User endpoints](docs/images/user-endpoint.png)
![Example request and response](docs/images/example-request.png)

</details>

## Architecture

```mermaid
flowchart LR
    Browser["Angular SPA<br/>guards + auth interceptor"] -->|"/api/v1<br/>Bearer JWT"| Error

    subgraph Backend["FastAPI"]
        Error["ErrorMiddleware<br/>uniform JSON errors"] --> Auth["AuthMiddleware<br/>JWT + role check"]
        Auth --> Routers["Routers<br/>auth, users"]
        Routers --> Services["Services<br/>business logic"]
        Services --> Repo["Repositories<br/>SQLAlchemy async"]
    end

    Repo --> DB[("PostgreSQL 17")]
    Config["YAML config<br/>+ env variables"] -.-> Backend
```

The backend is split by domain (`auth`, `user`, `config`, `db`), and each domain keeps the
same layers: router, service, repository, DTOs, exceptions, dependencies. Routers only
translate HTTP, services hold the rules, repositories talk to the database.

### Design notes

- **Authorization lives on the server.** Angular guards decide what to render, but
  `AuthMiddleware` checks the token and role on every request. Hiding a button is not the
  security boundary.
- **Access rules are data, not code.** The rule below in `backend/resources/default_config.yaml`
  is the whole definition of who can list users:

  ```yaml
  - path: /api/v1/users
    allowed_roles: [admin]
    methods: [GET, POST, PUT, DELETE]
  ```

- **Config is layered per environment.** `default_config.yaml` holds the base, and
  `local`, `test` and `prod` files override only what differs. Secrets come from
  environment variables.
- **Tests are tiered.** `unit` tests run without a database and gate merges into `dev`.
  The full suite, including `release` tests, gates merges into `main`.
- **The UI has a design system.** Views use `ds-*` classes from
  `frontend/src/app/design-system/` and never hard-code a color or size.

## Tech stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic v2, Uvicorn |
| Data | PostgreSQL 17, SQLAlchemy 2.0 (async), Alembic |
| Auth | PyJWT, Argon2 |
| Frontend | Angular 21 (standalone components, signals), SCSS design tokens |
| Tests | pytest with `unit` / `integration` / `release` markers, Vitest |
| Quality | Black, isort, mypy, GitHub Actions |
| Delivery | Docker multi-stage builds, Docker Compose, uv, Make |

## Getting started

### With Docker

```bash
git clone git@github.com:m-freelance/fastapi-angular-starter.git
cd fastapi-angular-starter
cp .env.example .env      # set JWT_SECRET_KEY and the database credentials

make up                   # or `make up-dev` for hot reload
make migrate              # or `make migrate-dev`
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Without Docker

Requires Python 3.14, [uv](https://docs.astral.sh/uv/) and a running PostgreSQL 17.

```bash
cd backend
uv sync

export DEPLOYMENT_TYPE=local
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
export JWT_SECRET_KEY=your-secret-key

cd ..
uv run --project backend uvicorn backend.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start                 # http://localhost:4200
```

See [frontend/README.md](frontend/README.md) for the route table and services.

## API endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/health` | Health check | public |
| `POST` | `/api/v1/auth/register` | Register a user | public |
| `POST` | `/api/v1/auth/login` | Log in, get a JWT | public |
| `GET` | `/api/v1/users/me` | Current user | user, admin |
| `GET` | `/api/v1/users` | Paginated user list | admin |

## Development

```bash
make help                 # all commands
make format               # apply Black and isort
make format-check         # check formatting
make compile-deps         # re-lock and sync backend dependencies

make test-local-unit      # fast tests, no database
make test-local           # full backend suite
make test                 # full suite in Docker

cd frontend && npm test   # frontend tests
```

Runtime dependencies go in `[project.dependencies]` in `backend/pyproject.toml`; test and
lint tools are in the `dev` group. `backend/uv.lock` is committed, so CI and Docker install
the same versions you do. More on the containers in [DOCKER.md](DOCKER.md).

## Configuration

| File | Purpose |
|------|---------|
| `default_config.yaml` | Base configuration |
| `local_config.yaml` | Local overrides (only the Angular dev server CORS origin, nothing secret) |
| `prod_config.yaml` | Production overrides, including hidden error details |
| `test_config.yaml` | Test overrides |

| Variable | Description | Required |
|----------|-------------|----------|
| `DEPLOYMENT_TYPE` | `local`, `prod` or `test` | yes |
| `DATABASE_URL` | PostgreSQL connection string | yes |
| `JWT_SECRET_KEY` | Secret for signing tokens | yes |
| `CONFIG_PATHS` | Extra config files, separated by `;` | no |

## Author

Mykyta Yaromenko, [GitHub](https://github.com/m-freelance)

## License

Apache License 2.0, see [LICENSE](LICENSE).
