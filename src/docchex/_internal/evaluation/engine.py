from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING

from docchex._internal.models import Document, Finding, Report, RuleResult

if TYPE_CHECKING:
    from docchex._internal.rules.base import Rule


class RuleEngine:
    """Runs a list of rules against a document and collects findings into a report."""

    rules: list[Rule]
    """The rules applied by this engine."""

    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules

    def run(self, doc: Document) -> Report:
        """Run all rules against the document and return a consolidated report."""
        findings: list[Finding] = []
        results: list[RuleResult] = []
        for rule in self.rules:
            rule_findings = rule.check(doc)
            if rule_findings:
                findings.extend(rule_findings)
                for f in rule_findings:
                    results.append(RuleResult(rule_id=f.rule_id, passed=False, finding=f))
            else:
                results.append(RuleResult(rule_id=rule.id, passed=True))
        return Report(document_path=str(doc.path), findings=findings, results=results)
