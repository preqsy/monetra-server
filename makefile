POETRY = poetry
VENV_PYTHON = $(shell poetry env info -p)/bin/python

.PHONY: worker run

worker:
	$(VENV_PYTHON) -m arq task_queue.main.WorkerSettings

run:
	$(VENV_PYTHON) -m uvicorn main:app --reload
