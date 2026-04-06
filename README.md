# docchex

Python core engine for document QA/QC. Parse documents, apply rule sets, run AI-assisted evaluation, and generate structured reports.

```python
from docchex import run_qaqc

result = run_qaqc(document, rules)
```

## Status

<!-- e.g. alpha / beta / stable -->

## Requirements

<!-- e.g. Python 3.12+, any non-obvious system deps -->

## Installation

```bash
pip install docchex
```

## Usage

### Run QA/QC on a PDF

```python
from docchex import run_qaqc

result = run_qaqc("report.pdf", "rules.yaml")

print(result["passed"])    # True / False
print(result["summary"])   # {"error": 1, "warning": 2, "info": 0}
print(result["findings"])  # list of individual rule violations
```

### Define rules in YAML

```yaml
# rules.yaml
rules:
  - id: check_introduction
    type: required_section
    match: Introduction
    severity: error

  - id: minimum_length
    type: word_count
    min: 500
    severity: warning
```

Rules can also be passed as a list of dicts directly:

```python
result = run_qaqc("report.pdf", [
    {"id": "check_intro", "type": "required_section", "match": "Introduction", "severity": "error"},
    {"id": "min_length",  "type": "word_count", "min": 500, "severity": "warning"},
])
```

### Result structure

```python
{
    "document": "report.pdf",
    "passed": False,
    "summary": {"error": 1, "warning": 0, "info": 0},
    "findings": [
        {
            "rule_id": "check_intro",
            "severity": "error",
            "message": "Required section not found: 'Introduction'",
            "location": None,
        }
    ],
}
```

### Built-in rule types

| Type | Parameters | Description |
|---|---|---|
| `required_section` | `match` (str) | Fails if the text is not found anywhere in the document |
| `word_count` | `min` (int), `max` (int) | Fails if the word count is outside the given bounds |

Both support a `severity` field: `error` (default for `required_section`), `warning` (default for `word_count`), or `info`.

## Documentation

Read the full documentation at [ashkans.github.io/docchex](https://ashkans.github.io/docchex/).

```bash
uv run python scripts/make docs
```

Serves the docs locally at `http://127.0.0.1:8000` with live reload.

## Evaluation

docchex ships with a versioned benchmark suite that measures end-to-end rule accuracy against committed document fixtures.

```bash
# first-time setup
uv run python scripts/make setup

# run benchmark suite
uv run python scripts/make eval
```

If `python` is not available in your shell, prefer the `uv run python ...` form above instead of `make eval`.

See the [Evaluation](https://ashkans.github.io/docchex/evaluation/) page in the docs for current results, how to add new cases, and the versioning workflow.

## License

<!-- e.g. MIT -->
