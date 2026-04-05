---
title: Dev Setup
---

## Prerequisites

You need [uv](https://github.com/astral-sh/uv) installed. If you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Clone and install

```bash
git clone https://github.com/ashkans/docchex
cd docchex
make setup
```

This installs all dependencies into a local virtual environment via `uv sync`.

## Running tasks

Tasks are run through `scripts/make.py`, invoked via `make`:

```bash
make format
make check
make test
```

Alternatively, you can call the script directly:

```bash
uv run python scripts/make.py format
```

## Common tasks

| Task | What it does |
|:-----|:-------------|
| `make format` | Auto-format the code |
| `make check` | Run all checks (quality, types, docs, API) |
| `make test` | Run the test suite |
| `make docs` | Serve docs locally at http://localhost:8000 |

## All tasks

| Category | Task | What it does |
|:---------|:-----|:-------------|
| Development | `format` | Auto-format the code |
| Development | `check` | Run all checks (quality, types, docs, API) |
| Development | `check-quality` | Lint with ruff |
| Development | `check-types` | Type-check with ty |
| Development | `check-docs` | Verify the documentation builds |
| Development | `check-api` | Check for API breaking changes |
| Development | `test` | Run the test suite |
| Development | `coverage` | Run tests and report coverage |
| Development | `eval` | Run the evaluation benchmark suite |
| Documentation | `docs` | Serve docs locally at http://localhost:8000 |
| Documentation | `docs-deploy` | Deploy docs to GitHub Pages |
| Release | `build` | Build source and wheel distributions |
| Release | `publish` | Publish to PyPI |
| Release | `changelog` | Update changelog from commits |
| Release | `release` | Full release (build + publish + changelog) |
| Utilities | `clean` | Delete build artifacts and cache files |
| Utilities | `vscode` | Configure VSCode for this project |
| Utilities | `setup` | Install all virtual environments |
