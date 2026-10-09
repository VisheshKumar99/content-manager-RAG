# Pip Command Helper

Quick reference for installing Python dependencies with pip.

| Command | Explanation |
|---------|-------------|
| `pip3 install -r requirements.txt` | Install every package listed in `requirements.txt`. |
| `pip3 install -r dependency.txt` | Same as above, but reads from a custom-named file `dependency.txt`. |
| `pip3 install <package>` | Install a single package by name. |
| `pip3 freeze > requirements.txt` | Save all currently installed packages (with versions) into `requirements.txt`. |
| `pip3 list` | List all installed packages. |
| `pip3 show <package>` | Show details about an installed package. |
| `pip3 uninstall <package>` | Remove an installed package. |
| `source .venv/bin/activate` | Activate the virtual environment (note: folder is `.venv`, not `venv`). |

## Flag notes

- `-r` is short for `--requirement` ("requirement", not "read"). It installs from a requirements file.
- `pip3` targets Python 3; `pip` points to whatever Python version is the system default.
