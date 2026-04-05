"""Tests for built-in rules and the rule loader."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from docchex._internal.models import Document
from docchex._internal.rules.builtin.required_section import RequiredSectionRule
from docchex._internal.rules.builtin.word_count import WordCountRule
from docchex._internal.rules.loader import RuleLoader


def _doc(text: str) -> Document:
    return Document(path=Path("test.pdf"), text=text, pages=[text])


# --- RequiredSectionRule ---


def test_required_section_passes_when_present() -> None:
    rule = RequiredSectionRule(rule_id="r1", match="Introduction")
    findings = rule.check(_doc("Introduction\nSome content here."))
    assert findings == []


def test_required_section_fails_when_missing() -> None:
    rule = RequiredSectionRule(rule_id="r1", match="Introduction")
    findings = rule.check(_doc("Conclusion\nSome content here."))
    assert len(findings) == 1
    assert findings[0].rule_id == "r1"
    assert findings[0].severity == "error"
    assert "Introduction" in findings[0].message


def test_required_section_case_insensitive() -> None:
    rule = RequiredSectionRule(rule_id="r1", match="Introduction")
    findings = rule.check(_doc("INTRODUCTION\nSome content."))
    assert findings == []


def test_required_section_custom_severity() -> None:
    rule = RequiredSectionRule(rule_id="r1", match="Abstract", severity="warning")
    findings = rule.check(_doc("No required heading found."))
    assert findings[0].severity == "warning"


def test_required_section_from_config() -> None:
    rule = RequiredSectionRule.from_config(
        {
            "id": "check_intro",
            "type": "required_section",
            "match": "Introduction",
            "severity": "error",
        },
    )
    assert rule.id == "check_intro"
    assert rule.match == "Introduction"
    assert rule.severity == "error"


# --- WordCountRule ---


def test_word_count_passes_when_above_min() -> None:
    rule = WordCountRule(rule_id="wc", min_words=3)
    findings = rule.check(_doc("one two three four"))
    assert findings == []


def test_word_count_fails_when_below_min() -> None:
    rule = WordCountRule(rule_id="wc", min_words=10)
    findings = rule.check(_doc("only three words"))
    assert len(findings) == 1
    assert "3" in findings[0].message
    assert "10" in findings[0].message


def test_word_count_fails_when_above_max() -> None:
    rule = WordCountRule(rule_id="wc", max_words=2)
    findings = rule.check(_doc("one two three"))
    assert len(findings) == 1
    assert "3" in findings[0].message
    assert "2" in findings[0].message


def test_word_count_passes_when_within_bounds() -> None:
    rule = WordCountRule(rule_id="wc", min_words=2, max_words=5)
    findings = rule.check(_doc("one two three"))
    assert findings == []


def test_word_count_no_bounds_always_passes() -> None:
    rule = WordCountRule(rule_id="wc")
    findings = rule.check(_doc("any amount of words here"))
    assert findings == []


def test_word_count_from_config() -> None:
    rule = WordCountRule.from_config(
        {
            "id": "length",
            "type": "word_count",
            "min": 100,
            "max": 5000,
            "severity": "warning",
        },
    )
    assert rule.id == "length"
    assert rule.min_words == 100
    assert rule.max_words == 5000
    assert rule.severity == "warning"


# --- RuleLoader ---


def test_loader_from_dicts() -> None:
    rules = RuleLoader().load(
        [
            {"id": "r1", "type": "required_section", "match": "Abstract"},
            {"id": "r2", "type": "word_count", "min": 50},
        ],
    )
    assert len(rules) == 2
    assert isinstance(rules[0], RequiredSectionRule)
    assert isinstance(rules[1], WordCountRule)


def test_loader_raises_on_unknown_type() -> None:
    with pytest.raises(ValueError, match="Unknown rule type"):
        RuleLoader().load([{"id": "r1", "type": "nonexistent_type"}])


def test_loader_from_yaml(tmp_path: Path) -> None:
    yaml_file = tmp_path / "rules.yaml"
    yaml_file.write_text(
        dedent("""\
        rules:
          - id: check_intro
            type: required_section
            match: Introduction
            severity: error
          - id: min_length
            type: word_count
            min: 200
            severity: warning
    """),
    )
    rules = RuleLoader().load(yaml_file)
    assert len(rules) == 2
    assert isinstance(rules[0], RequiredSectionRule)
    assert rules[0].match == "Introduction"
    assert isinstance(rules[1], WordCountRule)
    assert rules[1].min_words == 200


def test_loader_from_toml(tmp_path: Path) -> None:
    toml_file = tmp_path / "rules.toml"
    toml_file.write_text(
        dedent("""\
        [[rules]]
        id = "check_intro"
        type = "required_section"
        match = "Introduction"
        severity = "error"

        [[rules]]
        id = "min_length"
        type = "word_count"
        min = 100
        severity = "warning"
    """),
    )
    rules = RuleLoader().load(toml_file)
    assert len(rules) == 2
    assert isinstance(rules[0], RequiredSectionRule)
    assert isinstance(rules[1], WordCountRule)


def test_loader_raises_on_unsupported_extension(tmp_path: Path) -> None:
    bad_file = tmp_path / "rules.json"
    bad_file.write_text("{}")
    with pytest.raises(ValueError, match="Unsupported rule source"):
        RuleLoader().load(bad_file)
