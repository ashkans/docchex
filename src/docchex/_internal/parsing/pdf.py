from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING

from docchex._internal.models import Document
from docchex._internal.parsing.base import DocumentParser

if TYPE_CHECKING:
    from pathlib import Path


class PDFParser(DocumentParser):
    """Parse PDF files into Document objects using pdfplumber."""

    def parse(self, path: Path) -> Document:
        """Parse a PDF file into a Document, extracting text and metadata."""
        try:
            import pdfplumber  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError("pdfplumber is required to parse PDF files: pip install pdfplumber") from exc

        pages: list[str] = []
        metadata: dict = {}

        with pdfplumber.open(path) as pdf:
            metadata = pdf.metadata or {}
            pages.extend(page.extract_text() or "" for page in pdf.pages)

        text = "\n\n".join(pages)
        return Document(path=path, text=text, pages=pages, metadata=metadata)
