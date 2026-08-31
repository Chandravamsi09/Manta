.PHONY: install build run test lint clean docker-build

PYTHON ?= py
PORT ?= 8000

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

build:
	$(PYTHON) -m pip install -e .
	cd frontend && npm install && npm run build

run:
	$(PYTHON) main.py

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m ruff check manta/ tests/

docker-build:
	docker build -t manta-ml:latest -f Dockerfile .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
