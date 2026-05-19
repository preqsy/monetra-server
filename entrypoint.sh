#!/bin/sh
poetry run alembic upgrade head

poetry run tarsq --settings monetra_server.tarsq_settings.TarsqSettings --dashboard --port 9090 &

poetry run uvicorn monetra_server.main:app --host 0.0.0.0 --port 8000
