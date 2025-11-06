#!/bin/sh
poetry run alembic upgrade head

poetry run arq task_queue.main.WorkerSettings &

poetry run uvicorn main:app --host 0.0.0.0 --port 8000