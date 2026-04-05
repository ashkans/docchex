from __future__ import annotations

__all__ = ["Document", "Finding", "Report"]

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class Document:
    """A parsed document ready for rule evaluation."""

    path: Path
    """Path to the source file."""
    text: str
    """Full text content of the document."""
    pages: list[str]
    """Text content split by page."""
    metadata: dict[str, Any] = field(default_factory=dict)
    """Optional metadata extracted from the document (e.g. PDF metadata)."""


@dataclass
class Finding:
    """A single rule violation found in a document."""

    rule_id: str
    """ID of the rule that produced this finding."""
    severity: str
    """Severity level: ``"error"``, ``"warning"``, or ``"info"``."""
    message: str
    """Human-readable description of the violation."""
    location: str | None = None
    """Optional location reference within the document."""


@dataclass
class Report:
    """The result of running a set of rules against a document."""

    document_path: str
    """Path to the evaluated document."""
    findings: list[Finding]
    """All findings produced by the rule engine."""

    @property
    def passed(self) -> bool:
        """``True`` if no error-severity findings were produced."""
        return not any(f.severity == "error" for f in self.findings)

    @property
    def summary(self) -> dict[str, int]:
        """Finding counts grouped by severity."""
        counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Serialise the report to a plain dictionary."""
        return {
            "document": self.document_path,
            "passed": self.passed,
            "summary": self.summary,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "message": f.message,
                    "location": f.location,
                }
                for f in self.findings
            ],
        }
