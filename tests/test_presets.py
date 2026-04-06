"""Tests for built-in rule presets and multi-source loading."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

import docchex
from docchex._internal.rules.base import Rule
from docchex._internal.rules.loader import RuleLoader

# --- list_presets() ---


def test_list_presets_returns_expected_names() -> None:
    assert set(docchex.list_presets()) == {"tech_report", "academic_paper", "letter_email", "custom_template"}


def test_list_presets_is_sorted() -> None:
    presets = docchex.list_presets()
    assert presets == sorted(presets)


# --- Preset loading ---


@pytest.mark.parametrize("name", ["tech_report", "academic_paper", "letter_email", "custom_template"])
def test_each_preset_loads_rules(name: str) -> None:
    rules = RuleLoader().load(f"preset:{name}")
    assert isinstance(rules, list)
    assert len(rules) > 0
    assert all(isinstance(r, Rule) for r in rules)


def test_resolve_unknown_preset_raises() -> None:
    with pytest.raises(ValueError, match="Unknown preset"):
        RuleLoader().load("preset:nonexistent")


# --- Multi-source loading ---


def test_multi_source_two_yaml_files(tmp_path: Path) -> None:
    f1 = tmp_path / "a.yaml"
    f1.write_text("rules:\n  - {id: r1, type: required_section, match: Intro}\n")
    f2 = tmp_path / "b.yaml"
    f2.write_text("rules:\n  - {id: r2, type: word_count, min: 10}\n")

    rules = RuleLoader().load([str(f1), str(f2)])
    assert len(rules) == 2
    assert rules[0].id == "r1"
    assert rules[1].id == "r2"


def test_multi_source_preset_and_yaml(tmp_path: Path) -> None:
    extra = tmp_path / "extra.yaml"
    extra.write_text("rules:\n  - {id: extra.check, type: required_section, match: Appendix}\n")

    rules = RuleLoader().load(["preset:letter_email", str(extra)])
    ids = [r.id for r in rules]
    assert "extra.check" in ids
    assert "letter.salutation" in ids


def test_multi_source_preset_and_dicts() -> None:
    rules = RuleLoader().load([
        "preset:letter_email",
        [{"id": "custom.check", "type": "required_section", "match": "Re:"}],
    ])
    ids = [r.id for r in rules]
    assert "letter.salutation" in ids
    assert "custom.check" in ids


def test_multi_source_sources_are_ordered(tmp_path: Path) -> None:
    f1 = tmp_path / "first.yaml"
    f1.write_text("rules:\n  - {id: first, type: required_section, match: A}\n")
    f2 = tmp_path / "second.yaml"
    f2.write_text("rules:\n  - {id: second, type: required_section, match: B}\n")

    rules = RuleLoader().load([str(f1), str(f2)])
    assert rules[0].id == "first"
    assert rules[1].id == "second"


def test_multi_source_empty_list() -> None:
    assert RuleLoader().load([]) == []


# --- Backward compatibility ---


def test_single_dict_list_still_works() -> None:
    rules = RuleLoader().load([{"id": "r1", "type": "required_section", "match": "Intro"}])
    assert len(rules) == 1
    assert rules[0].id == "r1"


def test_single_string_path_still_works(tmp_path: Path) -> None:
    f = tmp_path / "rules.yaml"
    f.write_text("rules:\n  - {id: r1, type: required_section, match: Intro}\n")
    rules = RuleLoader().load(str(f))
    assert len(rules) == 1


def test_single_path_still_works(tmp_path: Path) -> None:
    f = tmp_path / "rules.yaml"
    f.write_text("rules:\n  - {id: r1, type: required_section, match: Intro}\n")
    rules = RuleLoader().load(f)
    assert len(rules) == 1


# --- run_qaqc integration ---


def test_run_qaqc_with_preset(tmp_path: Path) -> None:
    doc = tmp_path / "doc.txt"
    doc.write_text("Dear John,\n\nPlease find the attached report.\n\nRegards,\nAshkan")
    result = docchex.run_qaqc(str(doc), "preset:letter_email")
    assert isinstance(result, dict)
    assert "passed" in result
    assert "findings" in result


def test_run_qaqc_with_multi_source(tmp_path: Path) -> None:
    doc = tmp_path / "doc.txt"
    doc.write_text("Dear John,\n\nRegards,\nAshkan")
    extra = tmp_path / "extra.yaml"
    extra.write_text("rules:\n  - {id: extra.sig, type: required_section, match: Signature, severity: warning}\n")

    result = docchex.run_qaqc(str(doc), ["preset:letter_email", str(extra)])
    rule_ids = {f["rule_id"] for f in result["findings"]}
    assert "extra.sig" in rule_ids
