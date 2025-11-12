PY=python
PIP=pip

.PHONY: install dev fmt lint test smoke build

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	pre-commit install

fmt:
	black .
	isort .

lint:
	ruff .

test:
	pytest -q

smoke:
	$(PY) scripts/smoke_test.py

build:
	$(PY) -m build

