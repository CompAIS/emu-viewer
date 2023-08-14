# emu-viewer

## Local development setup

This README currently assumes you are on a unix based environment.

### Pre-requisites

You have `git` installed and have cloned this repository.

You have `make` installed:
- On windows:
  - If you have Chocolatey: `choco install make` in an admin terminal (recommended).
  - Direct install ([see here](https://gnuwin32.sourceforge.net/packages/make.htm))
  - See also: [stackoverflow](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows)
- Linux / WSL: `sudo apt install make`
- Mac: `brew install make`

You have [pyenv](https://github.com/pyenv/pyenv) installed (a Python version manager).

### Setup the project

For the purposes of the below, using Windows Subsystem for Linux does *not*
count as being "on windows".

1. If you have Python 3.11.4 already installed and you are not on windows, you should first uninstall that version. If you are on Windows, skip to step 3.
2. Install the tk headers with `make setup-tk`. Python needs to install after these headers are installed so it can compile with them. It's weird, I don't know.
3. Then install python 3.11.4 with `pyenv install 3.11.4`, and set your local python version with `pyenv local 3.11.4`. Confirm with `python --version`.
4. Run `make setup-dev`. This sets up your python virtual environment and installs the pip requirements in it.
5. Activate the virtual environment in your terminal:
   1. Windows: `.\venv\Scripts\activate`
   2. Mac / Linux: `source venv/bin/activate`

To leave the virtual environment, run `deactivate`.

Run the program with `make start`.

Build the program with `make build`.

### Code Style, Formatting, and Tests

!TODO

## Troubleshooting

https://stackoverflow.com/a/31299142