"""Tests for the rule engine and run_qaqc integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import docchex
from docchex._internal.evaluation.engine import RuleEngine
from docchex._internal.models import Document
from docchex._internal.rules.base import Rule
from docchex._internal.rules.builtin.required_section import RequiredSectionRule
from docchex._internal.rules.builtin.word_count import WordCountRule


def _doc(text: str) -> Document:
    return Document(path=Path("test.pdf"), text=text, pages=[text])


# --- RuleEngine ---


def test_engine_no_rules_returns_empty_report() -> None:
    engine = RuleEngine(rules=[])
    report = engine.run(_doc("some text"))
    assert report.findings == []
    assert report.passed is True


def test_engine_collects_findings_from_all_rules() -> None:
    rules: list[Rule] = [
        RequiredSectionRule(rule_id="r1", match="Introduction"),
        WordCountRule(rule_id="r2", min_words=1000),
    ]
    engine = RuleEngine(rules=rules)
    report = engine.run(_doc("short text without the required heading"))
    rule_ids = {f.rule_id for f in report.findings}
    assert "r1" in rule_ids
    assert "r2" in rule_ids


def test_engine_passes_when_all_rules_satisfied() -> None:
    rules: list[Rule] = [
        RequiredSectionRule(rule_id="r1", match="Introduction"),
        WordCountRule(rule_id="r2", min_words=2),
    ]
    engine = RuleEngine(rules=rules)
    report = engine.run(_doc("Introduction This is a valid document with enough words."))
    assert report.passed is True
    assert report.findings == []


def test_engine_document_path_in_report() -> None:
    engine = RuleEngine(rules=[])
    doc = Document(path=Path("/some/file.pdf"), text="text", pages=["text"])
    report = engine.run(doc)
    assert report.document_path == "/some/file.pdf"


# --- run_qaqc integration (PDF parser mocked) ---


def _make_mock_pdf_parser(text: str) -> MagicMock:
    mock_parser = MagicMock()
    mock_parser.parse.return_value = Document(
        path=Path("fake.pdf"),
        text=text,
        pages=[text],
    )
    return mock_parser


def test_run_qaqc_returns_dict() -> None:
    with patch("docchex._internal.parsing.pdf.PDFParser") as mock_parser:
        mock_parser.return_value = _make_mock_pdf_parser("Introduction Some text here.")
        result = docchex.run_qaqc(
            "fake.pdf",
            [{"id": "r1", "type": "required_section", "match": "Introduction"}],
        )
    assert isinstance(result, dict)
    assert "passed" in result
    assert "findings" in result
    assert "summary" in result
    assert "document" in result


def test_run_qaqc_passes_with_satisfied_rules() -> None:
    with patch("docchex._internal.parsing.pdf.PDFParser") as mock_parser:
        mock_parser.return_value = _make_mock_pdf_parser("Introduction Hello world text.")
        result = docchex.run_qaqc(
            "fake.pdf",
            [{"id": "r1", "type": "required_section", "match": "Introduction"}],
        )
    assert result["passed"] is True
    assert result["findings"] == []


def test_run_qaqc_fails_with_violated_rules() -> None:
    with patch("docchex._internal.parsing.pdf.PDFParser") as mock_parser:
        mock_parser.return_value = _make_mock_pdf_parser("No required section here.")
        result = docchex.run_qaqc(
            "fake.pdf",
            [{"id": "r1", "type": "required_section", "match": "Introduction", "severity": "error"}],
        )
    assert result["passed"] is False
    assert len(result["findings"]) == 1
    assert result["findings"][0]["rule_id"] == "r1"


def test_run_qaqc_raises_for_unsupported_format() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        docchex.run_qaqc("document.docx", [])
