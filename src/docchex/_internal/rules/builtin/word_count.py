from __future__ import annotations

__all__ = []

from typing import Any

from docchex._internal.models import Document, Finding
from docchex._internal.rules.base import Rule, Severity


class WordCountRule(Rule):
    """Checks that the document word count falls within optional min/max bounds."""

    id: str
    """Rule identifier."""
    min_words: int | None
    """Minimum word count required, or ``None`` for no lower bound."""
    max_words: int | None
    """Maximum word count allowed, or ``None`` for no upper bound."""
    severity: str
    """Severity of findings produced by this rule."""

    def __init__(
        self,
        rule_id: str,
        min_words: int | None = None,
        max_words: int | None = None,
        severity: str = Severity.WARNING,
    ) -> None:
        self.id = rule_id
        self.min_words = min_words
        self.max_words = max_words
        self.severity = severity

    def check(self, doc: Document) -> list[Finding]:
        """Return findings if the document word count is outside the configured bounds."""
        count = len(doc.text.split())
        findings: list[Finding] = []
        if self.min_words is not None and count < self.min_words:
            findings.append(
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message=f"Document has {count} words; minimum required is {self.min_words}.",
                ),
            )
        if self.max_words is not None and count > self.max_words:
            findings.append(
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message=f"Document has {count} words; maximum allowed is {self.max_words}.",
                ),
            )
        return findings

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> WordCountRule:
        """Instantiate from a rule configuration dictionary."""
        return cls(
            rule_id=config["id"],
            min_words=config.get("min"),
            max_words=config.get("max"),
            severity=config.get("severity", Severity.WARNING),
        )
