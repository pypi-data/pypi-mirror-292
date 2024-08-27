# JupyterLab Display Name

JupyterLab server extension that adds a display name field to the login page.

## Installation

Install the latest version of JupyterLab Display Name using pip:

```
pip install -U jupyterlab-display-name --extra-index-url https://painterqubits.github.io/jupyterlab-display-name/releases
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
