VENV_NAME ?= venv

ifeq ($(OS),Windows_NT)
	OS_TYPE := Windows
	SEP := \\
	BIN := $(VENV_NAME)\\Scripts
	PYTHON := $(BIN)\\python.exe
	PRECOMMIT := $(BIN)\\pre-commit.exe
	ENTRY := src\\main.py

	RM := rmdir /s /q
else
	OS_TYPE := $(shell uname -s)
	SEP := /
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
	$(PYTHON) -m src.main

.PHONY: build
build:
# 	lots of nonsense here
#   - astroquery requires the CITATION file but for some reason it doesn't automatically get added in
#   - we need to for some reason copy the Pillow metadata in, otherwise astropy hats us
#   - need to copy in our resources of course, this isn't nonsense
	$(PYTHON) -m PyInstaller $(ENTRY) \
		--name "EMU Viewer" \
        --icon resources$(SEP)assets$(SEP)favicon-32x32.png \
		--add-data resources$(SEP)assets:resources$(SEP)assets \
		--add-data resources$(SEP)CITATION:astroquery \
		--copy-metadata Pillow \
		--noconfirm --onedir --windowed

.PHONY: lint
lint:
	$(PYTHON) -m black . --check
	$(PYTHON) -m isort . --check
	$(PYTHON) -m autoflake . --check

.PHONY: fmt
fmt:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m autoflake .

.PHONY: test
test:
	$(PYTHON) -m pytest tests