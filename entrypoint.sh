#!/bin/sh
set -e
export RELEASE_VERSION=`sed -n 's/^ *version.*=.*"\([^"]*\)".*/\1/p' pyproject.toml`
poetry run alembic upgrade head

# Launch uvicorn and replace the caller as Process #1 in the container
exec "$@"