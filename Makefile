VENV_NAME ?= venv

ifeq ($(OS),Windows_NT)
	OS_TYPE := Windows
	BIN := $(VENV_NAME)\\Scripts
	PYTHON := $(BIN)\\python.exe
	PRECOMMIT := $(BIN)\\pre-commit.exe
	ENTRY := src\\main.py
	RM := rmdir /s /q
else
	OS_TYPE := $(shell uname -s)
	BIN := $(VENV_NAME)/bin
	PYTHON := $(BIN)/python
	PRECOMMIT := $(BIN)/pre-commit
	ENTRY := ./src/main.py
	RM := rm -rf
endif

.PHONY: setup-tk
setup-tk:
ifeq ($(OS_TYPE),Linux)
	sudo apt-get update
	sudo apt-get install python3 python3-venv python3-tk python3-tk tk-dev
else ifeq ($(OS_TYPE),Darwin)
	brew install python-tk
endif

.PHONY: venv
venv:
	python -m venv $(VENV_NAME)

.PHONY: setup
setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: setup-dev
setup-dev: setup
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PRECOMMIT) install

.PHONY: venv-clean
venv-clean:
	-$(RM) $(VENV_NAME)

.PHONY: clean
clean:
	-$(RM) build
	-$(RM) dist

.PHONY: start
start:
	$(PYTHON) $(ENTRY)

.PHONY: build
build:
	$(PYTHON) -m PyInstaller $(ENTRY)

.PHONY: lint
lint:
	$(PYTHON) -m black . --check
	$(PYTHON) -m autoflake . --check
	$(PYTHON) -m isort . --check

.PHONY: fmt
fmt:
	$(PYTHON) -m black .
	$(PYTHON) -m autoflake .
	$(PYTHON) -m isort .

.PHONY: test
test:
	$(PYTHON) -m pytest tests