


.phony setup-py
setup-py:
	python -m venv venv
	# assuming windows
	venv\Scripts\activate.bat
	python -m pip install -r requirements.txt

.phony venv-deactivate:
venv-deactivate:
	venv\Scripts\deactivate.bat