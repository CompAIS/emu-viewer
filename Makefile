VENV_NAME?=venv
PYTHON=$(VENV_NAME)/bin/python

.phony: setup
setup:
	sudo apt-get update
	sudo apt-get install python3 python3-venv
	python3 -m venv venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

.phony: setup-dev
setup-dev: setup
	$(PYTHON) -m pip install -r requirements-dev.txt

.phony: venv-clean
venv-clean:
	rm -rf venv