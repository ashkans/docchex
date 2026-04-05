from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING

from docchex._internal.models import Document
from docchex._internal.parsing.base import DocumentParser

if TYPE_CHECKING:
    from pathlib import Path


class TextParser(DocumentParser):
    """Parse plain-text (.txt) files into Document objects.

    Pages are split on double newlines, mirroring PDFParser's convention.
    Used primarily for eval fixtures to keep CI dependency-free.
    """

    def parse(self, path: Path) -> Document:
        """Parse a plain-text file into a Document, splitting pages on double newlines."""
        text = path.read_text(encoding="utf-8")
        pages = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not pages:
            pages = [""]
        return Document(path=path, text=text, pages=pages, metadata={})
