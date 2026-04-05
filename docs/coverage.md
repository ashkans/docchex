# Test Coverage

Coverage is measured on every push to `main` and the results are committed to `reports/coverage.json`.

## Summary

```python exec="true" source="tabbed-left"
import json
from pathlib import Path

def format_coverage(pct: float) -> str:
    if pct == 100:
        return "✅ 100.0%"
    elif pct >= 80:
        return f"🟡 {pct:.1f}%"
    else:
        return f"🔴 {pct:.1f}%"

report_path = Path("reports/coverage.json")

if not report_path.exists():
    print("*No coverage data yet — run `make test` to generate it.*")
else:
    data = json.loads(report_path.read_text())
    totals = data["totals"]
    pct = totals["percent_covered"]
    covered = totals["covered_lines"]
    total = totals["num_statements"]

    print(f"**Overall coverage:** `{pct:.1f}%` ({covered}/{total} statements)\n")

    rows = [
        (
            path.replace("src/", "").replace("/", ".").removesuffix(".py"),
            info["summary"]["covered_lines"],
            info["summary"]["num_statements"],
            info["summary"]["percent_covered"],
        )
        for path, info in sorted(data["files"].items())
        if "src/" in path
    ]

    print("| Module | Covered | Statements | Coverage |")
    print("|:-------|--------:|-----------:|:---------|")
    for module, covered, stmts, pct_m in rows:
        print(f"| `{module}` | {covered} | {stmts} | {format_coverage(pct_m)} |")
```
