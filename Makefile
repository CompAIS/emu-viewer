VENV_NAME ?= venv

ifeq ($(OS),Windows_NT)
    # Windows-specific settings
    OS_TYPE := Windows
    PYTHON := $(VENV_NAME)\\Scripts\\python.exe
    ENTRY := src\\main.py
else
    # Unix-like systems settings
	OS_TYPE := $(shell uname -s)
    PYTHON := $(VENV_NAME)/bin/python
    ENTRY := ./src/main.py
endif


.PHONY: setup-tk
setup-tk:
ifeq ($(OS_TYPE),Linux)
	sudo apt-get update
	sudo apt-get install python3 python3-venv python3-tk python3-tk tk-dev
else ifeq ($(OS_TYPE),Darwin)
	brew install python-tk
endif

.phony: venv
venv:
	python -m venv venv

.phony: setup
setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

.phony: setup-dev
setup-dev: setup
	$(PYTHON) -m pip install -r requirements-dev.txt
	pre-commit install

.phony: venv-clean
venv-clean:
	rm -rf venv

.phony: clean
clean:
	rm -rf build
	rm -rf dist

.phony: start
start:
	$(PYTHON) $(ENTRY)

.phony: build
build: clean
	$(PYTHON) -m PyInstaller $(ENTRY)

.phony: lint
lint:
	$(PYTHON) -m black . --check

.phony: fmt
fmt:
	$(PYTHON) -m black .

.phony: test
test:
	$(PYTHON) -m pytest tests