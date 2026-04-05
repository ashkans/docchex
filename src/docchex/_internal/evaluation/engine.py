from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING

from docchex._internal.models import Document, Finding, Report

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
        for rule in self.rules:
            findings.extend(rule.check(doc))
        return Report(document_path=str(doc.path), findings=findings)
