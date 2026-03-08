# Instructions for Coding Agents

- use `uv` to run tools like `ruff` or `pytest` (eg `uv run ruff format`)
- use `uv run python` to run Python in the virtual environment of the project
- use `uv run script.py` to run a script in the virtual environment of the project
  - alternatively add shebang `#!/usr/bin/env -S uv run` and make script executable
- after completing a task, run:
  - formatting: `uv run ruff format`
  - linting: `uv run ruff check`
  - testing: `uv run pytest`
