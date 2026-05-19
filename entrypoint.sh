#!/bin/sh
poetry run alembic upgrade head

poetry run tarsq --settings tarsq_settings.TarsqSettings --dashboard --port 9090 &

poetry run uvicorn main:app --host 0.0.0.0 --port 8000