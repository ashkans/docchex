# Evaluation

`docchex` ships with a versioned evaluation suite that measures end-to-end accuracy — whether the rule engine correctly processes known documents and produces the expected findings.

The eval suite is **separate from unit tests**: rather than asserting pass/fail on isolated logic, it benchmarks the full pipeline against committed document fixtures.

## Current Results

```python exec="true" source="tabbed-left"
import json
from pathlib import Path

data = json.loads(Path("evals/results/latest.json").read_text())

print(f"**Eval suite:** `v{data['eval_version']}`  ")
print(f"**Package:** `v{data['package_version']}`  ")
print(f"**Last run:** `{data['timestamp']}`  ")
print(f"**Overall accuracy:** `{data['accuracy']:.1%}` ({data['passed']}/{data['total']} cases)\n")

if data["by_suite"]:
    print("| Suite | Total | Passed | Accuracy |")
    print("|---|---|---|---|")
    for suite, s in data["by_suite"].items():
        print(f"| `{suite}` | {s['total']} | {s['passed']} | {s['accuracy']:.1%} |")
else:
    print("*No results yet — run `make eval` to generate them.*")
```

## How It Works

The runner lives in `evals/runner.py`. On each push to `main` it:

1. Discovers all `*.yaml` files under `evals/cases/` alphabetically.
2. For each case, parses the fixture document, applies the inline rule definitions, and compares engine output against declared expectations.
3. Writes results to `evals/results/latest.json` (committed back to the repo) and uploads it as a GitHub Actions artifact.

Document fixtures are plain `.txt` files — no PDFs required in CI. The `TextParser` handles them directly.

## Adding a New Eval Case

1. Add or edit a YAML file in `evals/cases/`. Each case needs:

    ```yaml
    version: "1"
    suite: my_suite
    cases:
      - id: my_case
        document: data/documents/my_fixture.txt  # relative to evals/
        rules:
          - {id: r1, type: required_section, match: Overview, severity: error}
        expected:
          passed: false
          findings_count: 1
          findings:
            - {rule_id: r1, severity: error}
    ```

2. Add any new fixture documents to `evals/data/documents/`.

3. Bump `evals/VERSION` (see versioning below).

4. Run locally: `make eval`

## Versioning

`evals/VERSION` is the single source of truth for the eval suite version. It is embedded in every `latest.json` so results can be correlated with the cases that produced them.

| Change | Bump |
|---|---|
| Fix a broken case or fixture typo | Patch (`1.0.0` → `1.0.1`) |
| New cases added to an existing suite | Minor (`1.0.x` → `1.1.0`) |
| New suite file added | Minor |
| Results schema changed | Major (`x.0.0`) |

Bump by editing `evals/VERSION` and committing:

```bash
# Edit evals/VERSION to "1.1.0"
git add evals/VERSION
git commit -m "eval: bump suite to 1.1.0 — add new cases"
```

## Running Locally

```bash
# Run all suites
make eval

# Run directly
uv run python evals/runner.py

# Run a single suite
uv run python evals/runner.py --suite required_section

# Write a history snapshot
uv run python evals/runner.py --history

# Informational run (exit 0 even on failures)
uv run python evals/runner.py --no-strict
```

History snapshots are written to `evals/results/history/` and are gitignored. The `latest.json` is always committed.
