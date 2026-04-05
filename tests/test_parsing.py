"""Tests for document parsers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docchex._internal.parsing.base import DocumentParser
from docchex._internal.parsing.pdf import PDFParser

# --- DocumentParser.for_path factory ---


def test_for_path_returns_pdf_parser_for_pdf() -> None:
    parser = DocumentParser.for_path(Path("report.pdf"))
    assert isinstance(parser, PDFParser)


def test_for_path_raises_for_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        DocumentParser.for_path(Path("report.docx"))


def test_for_path_case_insensitive_extension() -> None:
    parser = DocumentParser.for_path(Path("report.PDF"))
    assert isinstance(parser, PDFParser)


# --- PDFParser ---


def _make_pdfplumber_mock(pages_text: list[str], metadata: dict | None = None) -> MagicMock:
    def mock_page(text: str) -> MagicMock:
        return MagicMock(**{"extract_text.return_value": text})

    mock_pdf = MagicMock()
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [mock_page(t) for t in pages_text]
    mock_pdf.metadata = metadata or {}
    return mock_pdf


def test_pdf_parser_extracts_text() -> None:
    mock_pdf = _make_pdfplumber_mock(["Page one content.", "Page two content."])
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("test.pdf"))
    assert "Page one content." in doc.text
    assert "Page two content." in doc.text


def test_pdf_parser_returns_document_with_pages() -> None:
    mock_pdf = _make_pdfplumber_mock(["First page.", "Second page."])
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("test.pdf"))
    assert len(doc.pages) == 2
    assert doc.pages[0] == "First page."
    assert doc.pages[1] == "Second page."


def test_pdf_parser_joins_pages_with_double_newline() -> None:
    mock_pdf = _make_pdfplumber_mock(["Page A.", "Page B."])
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("test.pdf"))
    assert doc.text == "Page A.\n\nPage B."


def test_pdf_parser_handles_empty_page() -> None:
    mock_pdf = _make_pdfplumber_mock(["Content.", None])  # None simulates extract_text returning None
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("test.pdf"))
    assert doc.pages[1] == ""


def test_pdf_parser_sets_path() -> None:
    mock_pdf = _make_pdfplumber_mock(["text"])
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("/some/path/file.pdf"))
    assert doc.path == Path("/some/path/file.pdf")


def test_pdf_parser_captures_metadata() -> None:
    mock_pdf = _make_pdfplumber_mock(["text"], metadata={"Author": "Jane Doe", "Title": "Report"})
    with patch("pdfplumber.open", return_value=mock_pdf):
        doc = PDFParser().parse(Path("test.pdf"))
    assert doc.metadata["Author"] == "Jane Doe"
    assert doc.metadata["Title"] == "Report"


def test_pdf_parser_raises_import_error_without_pdfplumber() -> None:
    with patch.dict("sys.modules", {"pdfplumber": None}), pytest.raises(ImportError, match="pdfplumber"):
        PDFParser().parse(Path("test.pdf"))
