# Monetra Server (Backend)

Backend for Monetra built with FastAPI, SQLAlchemy and Alembic.

This repository provides the REST API, background worker (ARQ), database models and migrations, and integrations for Firebase, Plaid, Mono, and exchange rate APIs.

## Quick overview

- Framework: FastAPI
- ORM: SQLAlchemy
- Migrations: Alembic
- Task queue: ARQ
- Python (poetry): 3.12.x (pyproject.toml lists ^3.12.3)

## Prerequisites

- Python 3.12.x
- Poetry (for dependency management)
- Postgres (or a compatible DATABASE_URL)
- Redis (for ARQ task queue)
- Optional: Docker & Docker Engine (for containerized runs)

## Environment

Copy the example env and edit values:

```bash
cp .env.example .env
# then edit .env and provide values for DATABASE_URL, REDIS_*, FIREBASE path, PLAID, MONO, etc.
```

Important environment variables (present in `.env.example`):

- DOMAIN, SUBDOMAIN, ACME_EMAIL — domain/acme configuration
- DATABASE_URL — e.g. postgresql://user:pass@host:5432/dbname
- REDIS_HOST, REDIS_PORT, REDIS_PASSWORD — for ARQ
- FIREBASE_ADMIN_SDK_JSON_PATH — path inside container to Firebase admin JSON
- MONO_BASE_URL, MONO_SECRET_KEY — Mono integration
- PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV — Plaid integration
- EXCHANGE_API_KEY, EXCHANGE_RATE_BASE_URL — exchange rates

If you run in Docker, mount the Firebase admin JSON (or set FIREBASE_ADMIN_SDK_JSON_PATH to the mounted path).

## Install dependencies (local / dev)

Install with Poetry:

```bash
poetry install
```

If you don't use Poetry, create a virtualenv and install dependencies from `pyproject.toml` using an alternative tool (not covered here).

## Run locally (development)

Ensure `.env` is configured and your database & redis are reachable.

Run the app with auto-reload:

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This starts FastAPI at http://0.0.0.0:8000 and exposes the OpenAPI docs at `/docs`.

To run the ARQ worker manually (if you don't want it started in the background):

```bash
poetry run arq task_queue.main.WorkerSettings
```

## Docker

Build the image:

```bash
docker build -t monetra-server .
```

Run the container (example using an env file):

```bash
docker run --env-file .env -p 8000:8000 --name monetra-server monetra-server
```

The repository's `Dockerfile` sets `/app` as the working directory and the `entrypoint.sh` will:

- run `alembic upgrade head` to apply migrations
- start the ARQ worker in the background
- run `uvicorn main:app` to start the API server

So the container will be ready to serve after it boots (provided it can reach the DB/Redis and env variables are correct).

## Database migrations

Create a new migration (autogenerate):

```bash
poetry run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

If running in Docker, the container's `entrypoint.sh` already runs `alembic upgrade head` on start.

## Seeding data

There are small scripts to seed initial data. For example, to seed subscription plans & features:

```bash
poetry run python scripts/seed_subscriptions.py
```

## Running tests / type checking

- The project includes `mypy` as a dependency in `pyproject.toml`. Run:

```bash
poetry run mypy .
```

(No test runner or tests are included in the repository root; add tests under a `tests/` directory if needed.)

## Common developer tasks

- Start local server with auto-reload: `poetry run uvicorn main:app --reload`
- Run migrations: `poetry run alembic upgrade head`
- Generate a migration: `poetry run alembic revision --autogenerate -m "msg"`
- Seed subscriptions: `poetry run python scripts/seed_subscriptions.py`
- Start ARQ worker: `poetry run arq task_queue.main.WorkerSettings`

## Helpful notes & troubleshooting

- If migrations fail, verify `DATABASE_URL` and database accessibility.
- If ARQ cannot connect, verify Redis host/port and password.
- Firebase initialization expects the JSON service account available at the path configured by `FIREBASE_ADMIN_SDK_JSON_PATH`.
- Use logs from `docker logs monetra-server` to inspect container startup problems.

## Contributing

1. Fork the repo and create a feature branch
2. Add tests for new behavior where appropriate
3. Run `mypy` and make sure static checks pass
4. Create an Alembic migration if DB models changed
