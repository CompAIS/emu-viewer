VENV_NAME?=venv
PYTHON=$(VENV_NAME)/bin/python

.phony: setup-py-wsl
setup-py-wsl:
	sudo apt-get update
	sudo apt-get install python3 python3-venv python3-tk python3-tk tk-dev

.phony: setup-py-mac
setup-py-mac:
	brew install python-tk

.phony: setup
setup:
	python3 -m venv venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

.phony: setup-dev
setup-dev: setup
	$(PYTHON) -m pip install -r requirements-dev.txt

.phony: venv-clean
venv-clean:
	rm -rf venv

.phony: clean
clean:
	rm -rf build
	rm -rf dist

.phony: build
build: clean
	$(PYTHON) -m PyInstaller ./src/main.py

.phony: lint
lint:
	$(PYTHON) -m black . --check

.phony: fmt
fmt:
	$(PYTHON) -m black .

.phony: test
test:
	$(PYTHON) -m pytest tests