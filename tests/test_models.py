"""Tests for core data models."""

from __future__ import annotations

from pathlib import Path

from docchex._internal.models import Document, Finding, Report


def _doc(text: str = "hello world") -> Document:
    return Document(path=Path("test.pdf"), text=text, pages=[text])


def test_report_passed_when_no_errors() -> None:
    report = Report(
        document_path="test.pdf",
        findings=[
            Finding(rule_id="r1", severity="warning", message="minor issue"),
        ],
    )
    assert report.passed is True


def test_report_fails_when_has_error() -> None:
    report = Report(
        document_path="test.pdf",
        findings=[
            Finding(rule_id="r1", severity="error", message="bad"),
        ],
    )
    assert report.passed is False


def test_report_passed_with_no_findings() -> None:
    report = Report(document_path="test.pdf", findings=[])
    assert report.passed is True


def test_report_summary_counts() -> None:
    report = Report(
        document_path="test.pdf",
        findings=[
            Finding(rule_id="r1", severity="error", message="e1"),
            Finding(rule_id="r2", severity="error", message="e2"),
            Finding(rule_id="r3", severity="warning", message="w1"),
        ],
    )
    assert report.summary == {"error": 2, "warning": 1, "info": 0}


def test_report_to_dict_structure() -> None:
    report = Report(
        document_path="test.pdf",
        findings=[Finding(rule_id="r1", severity="warning", message="msg", location="page 1")],
    )
    d = report.to_dict()
    assert d["document"] == "test.pdf"
    assert d["passed"] is True
    assert d["summary"]["warning"] == 1
    assert len(d["findings"]) == 1
    assert d["findings"][0] == {
        "rule_id": "r1",
        "severity": "warning",
        "message": "msg",
        "location": "page 1",
    }


def test_finding_location_defaults_to_none() -> None:
    f = Finding(rule_id="r1", severity="info", message="ok")
    assert f.location is None
