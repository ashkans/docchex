from __future__ import annotations

__all__ = ["DocumentParser"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from docchex._internal.models import Document


class DocumentParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(self, path: Path) -> Document:
        """Parse the file at the given path into a Document."""
        ...

    @classmethod
    def for_path(cls, path: Path) -> DocumentParser:
        """Return the appropriate parser for the given file path based on its extension."""
        from docchex._internal.parsing.pdf import PDFParser  # noqa: PLC0415
        from docchex._internal.parsing.text import TextParser  # noqa: PLC0415

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return PDFParser()
        if suffix == ".txt":
            return TextParser()
        raise ValueError(f"Unsupported file type: {suffix!r}")
