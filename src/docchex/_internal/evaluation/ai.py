from __future__ import annotations

__all__ = ["AIEvaluator"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docchex._internal.models import Document, Finding


class AIEvaluator(ABC):
    """Stub interface for AI-assisted document evaluation.

    Implement this class to add AI-powered rule checking.
    The evaluate() method receives a Document and returns a list of Findings,
    just like a regular Rule — making it composable with RuleEngine.
    """

    @abstractmethod
    def evaluate(self, doc: Document) -> list[Finding]:
        """Evaluate the document and return a list of findings."""
        ...
