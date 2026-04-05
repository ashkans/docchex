from __future__ import annotations

__all__ = ["Rule", "Severity"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from docchex._internal.models import Document, Finding


class Severity:
    """Constants for rule severity levels."""

    ERROR = "error"
    """Blocks the document from passing."""
    WARNING = "warning"
    """Non-blocking issue worth noting."""
    INFO = "info"
    """Informational finding only."""


class Rule(ABC):
    """Abstract base class for all docchex rules."""

    id: str
    """Unique identifier for this rule."""
    severity: str = Severity.WARNING
    """Default severity level for findings produced by this rule."""

    @abstractmethod
    def check(self, doc: Document) -> list[Finding]:
        """Check the document and return any findings."""
        ...

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Rule:
        """Instantiate the rule from a configuration dictionary."""
        raise NotImplementedError(f"{cls.__name__} does not implement from_config")
