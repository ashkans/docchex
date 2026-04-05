from __future__ import annotations

__all__ = []

from typing import Any

from docchex._internal.models import Document, Finding
from docchex._internal.rules.base import Rule, Severity


class RequiredSectionRule(Rule):
    """Checks that a required section heading is present in the document."""

    id: str
    """Rule identifier."""
    match: str
    """The section heading text to search for (case-insensitive)."""
    severity: str
    """Severity of the finding when the section is missing."""

    def __init__(self, rule_id: str, match: str, severity: str = Severity.ERROR) -> None:
        self.id = rule_id
        self.match = match
        self.severity = severity

    def check(self, doc: Document) -> list[Finding]:
        """Return a finding if the required section is absent from the document."""
        if self.match.lower() not in doc.text.lower():
            return [
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message=f"Required section not found: {self.match!r}",
                ),
            ]
        return []

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> RequiredSectionRule:
        """Instantiate from a rule configuration dictionary."""
        return cls(
            rule_id=config["id"],
            match=config["match"],
            severity=config.get("severity", Severity.ERROR),
        )
