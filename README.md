# emu-viewer

## Local development setup

This README currently assumes you are on a unix based environment.

### Pre-requisites

You have `make` installed:

On windows: https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows
Linux / WSL: `sudo apt install make`
Mac: `brew install make`

### Setup the project

1. Run `make setup-dev`. This installs python and sets up your python environment.
1. Run `source venv/bin/activate`. This enables the virtual environment to use on your system.
1. Run `python main.py` to run the python program.

To leave the virtual environment, run `deactivate`.

## Troubleshooting

https://stackoverflow.com/a/31299142