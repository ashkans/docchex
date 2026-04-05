#!/usr/bin/env python3
"""Eval runner — discovers cases, runs them against docchex, writes results.

Usage:
    uv run python evals/runner.py [--output PATH] [--history] [--suite NAME] [--no-strict]

Exit codes:
    0  All eval cases passed (or --no-strict was passed).
    1  One or more eval cases failed.
    2  Runner error (bad case definition, missing file, etc.).
"""
from __future__ import annotations

import argparse
import datetime
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any

import yaml  # already a project dependency

EVALS_DIR = Path(__file__).parent
CASES_DIR = EVALS_DIR / "cases"
RESULTS_DIR = EVALS_DIR / "results"
HISTORY_DIR = RESULTS_DIR / "history"
VERSION_FILE = EVALS_DIR / "VERSION"


def _read_eval_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def _read_package_version() -> str:
    try:
        return importlib.metadata.version("docchex")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _load_cases_file(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _discover_case_files(suite_filter: str | None) -> list[Path]:
    files = sorted(CASES_DIR.glob("*.yaml"))
    if suite_filter:
        files = [f for f in files if f.stem == suite_filter]
    return files


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id: str = case["id"]
    doc_path = EVALS_DIR / case["document"]
    rules_raw: list[dict[str, Any]] = case["rules"]
    expected: dict[str, Any] = case["expected"]

    from docchex._internal.evaluation.engine import RuleEngine
    from docchex._internal.parsing.base import DocumentParser
    from docchex._internal.rules.loader import RuleLoader

    doc = DocumentParser.for_path(doc_path).parse(doc_path)
    rules = RuleLoader().load(rules_raw)
    report = RuleEngine(rules).run(doc)

    actual_findings = [
        {"rule_id": f.rule_id, "severity": f.severity, "message": f.message}
        for f in report.findings
    ]

    failures: list[str] = []

    if "passed" in expected and report.passed != expected["passed"]:
        failures.append(f"expected passed={expected['passed']}, got passed={report.passed}")

    if "findings_count" in expected and len(actual_findings) != expected["findings_count"]:
        failures.append(
            f"expected {expected['findings_count']} finding(s), got {len(actual_findings)}"
        )

    for exp in expected.get("findings", []):
        if not any(
            af["rule_id"] == exp["rule_id"] and af["severity"] == exp["severity"]
            for af in actual_findings
        ):
            failures.append(
                f"expected finding {{rule_id={exp['rule_id']!r}, severity={exp['severity']!r}}} not found"
            )

    return {
        "id": case_id,
        "passed": len(failures) == 0,
        "failure_reason": "; ".join(failures) if failures else None,
        "actual": {"passed": report.passed, "findings": actual_findings},
        "expected": expected,
    }


def _run_suite(suite_data: dict[str, Any]) -> dict[str, Any]:
    suite_name: str = suite_data["suite"]
    results: list[dict[str, Any]] = []

    for case in suite_data.get("cases", []):
        result = _evaluate_case(case)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        suffix = f"  → {result['failure_reason']}" if result["failure_reason"] else ""
        print(f"  [{status}] {suite_name}/{result['id']}{suffix}")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "suite": suite_name,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "failures": [r for r in results if not r["passed"]],
    }


def run(suite_filter: str | None = None) -> dict[str, Any]:
    case_files = _discover_case_files(suite_filter)
    if not case_files:
        print("No eval case files found.", file=sys.stderr)
        sys.exit(2)

    suite_results: list[dict[str, Any]] = []
    for case_file in case_files:
        suite_data = _load_cases_file(case_file)
        print(f"\nSuite: {suite_data['suite']}")
        suite_results.append(_run_suite(suite_data))

    total = sum(s["total"] for s in suite_results)
    passed = sum(s["passed"] for s in suite_results)

    return {
        "eval_version": _read_eval_version(),
        "package_version": _read_package_version(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "by_suite": {
            s["suite"]: {
                "total": s["total"],
                "passed": s["passed"],
                "failed": s["failed"],
                "accuracy": s["accuracy"],
            }
            for s in suite_results
        },
        "failures": [
            {"suite": s["suite"], **f}
            for s in suite_results
            for f in s["failures"]
        ],
    }


def _write_results(results: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {path}")


def _print_summary(results: dict[str, Any]) -> None:
    print(
        f"\n{'=' * 60}\n"
        f"Eval suite   : v{results['eval_version']}\n"
        f"Package      : v{results['package_version']}\n"
        f"Total cases  : {results['total']}\n"
        f"Passed       : {results['passed']}\n"
        f"Failed       : {results['failed']}\n"
        f"Accuracy     : {results['accuracy']:.1%}\n"
        f"{'=' * 60}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the docchex eval suite.")
    parser.add_argument(
        "--output",
        default=str(RESULTS_DIR / "latest.json"),
        help="Path to write results JSON (default: evals/results/latest.json)",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        default=False,
        help="Also write a timestamped snapshot to evals/results/history/.",
    )
    parser.add_argument(
        "--suite",
        default=None,
        help="Run only this suite (must match a case filename stem).",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        default=False,
        help="Exit 0 even when cases fail (informational runs).",
    )
    args = parser.parse_args()

    results = run(suite_filter=args.suite)
    _print_summary(results)

    output_path = Path(args.output)
    _write_results(results, output_path)

    if args.history:
        ts = results["timestamp"][:16].replace("T", "_").replace(":", "-")
        history_name = f"{ts}_v{results['eval_version']}.json"
        _write_results(results, HISTORY_DIR / history_name)

    if results["failed"] > 0 and not args.no_strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
