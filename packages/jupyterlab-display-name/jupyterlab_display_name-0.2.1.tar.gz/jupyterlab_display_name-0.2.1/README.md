# JupyterLab Display Name

[![PyPI Latest Release](https://img.shields.io/pypi/v/jupyterlab-display-name)](https://pypi.org/project/jupyterlab-display-name/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/jupyterlab-display-name)](https://pypi.org/project/jupyterlab-display-name/)
[![License](https://img.shields.io/pypi/l/jupyterlab-display-name)](https://github.com/PainterQubits/jupyterlab-display-name/blob/main/LICENSE)
[![CI](https://github.com/PainterQubits/jupyterlab-display-name/actions/workflows/ci.yml/badge.svg)](https://github.com/PainterQubits/jupyterlab-display-name/actions/workflows/ci.yml)

JupyterLab server extension that adds a display name field to the login page.

## Installation

Install the latest version of JupyterLab Display Name using pip:

```
pip install -U jupyterlab-display-name
```

This extension should run alongside
[JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
version 4.

## Development

To develop, the following dependencies must be installed:

- [Python](https://www.python.org/downloads/)
- [Hatch](https://hatch.pypa.io/latest/install/)

To run JupyterLab with this extension, run:

```
hatch run jupyter lab
```

If the server extension code changes, the server will need to be restarted.
