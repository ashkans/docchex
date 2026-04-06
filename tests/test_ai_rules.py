"""Tests for AICheckRule, LLMClient protocol, and provider import guards."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from docchex import (
    AICheckRule,
    AnthropicClient,
    LLMClient,
    LLMResponse,
    OllamaClient,
    OpenAIClient,
    RuleLoader,
    run_qaqc,
)
from docchex._internal.models import Document

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc(text: str = "Hello world") -> Document:
    return Document(path=Path("test.txt"), text=text, pages=[text], metadata={})


class _MockLLM:
    """Minimal LLMClient duck-type for tests."""

    def __init__(self, *, passed: bool = True, reason: str = "ok") -> None:
        self._response = LLMResponse(passed=passed, reason=reason)
        self.calls: list[tuple[Document, str]] = []

    def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
        self.calls.append((doc, prompt))
        return self._response


# ---------------------------------------------------------------------------
# AICheckRule unit tests
# ---------------------------------------------------------------------------

def test_ai_check_rule_passes() -> None:
    llm = _MockLLM(passed=True, reason="Looks good")
    rule = AICheckRule(rule_id="test.pass", prompt="Is this a greeting?", llm=llm)
    findings = rule.check(_make_doc())
    assert findings == []
    assert len(llm.calls) == 1


def test_ai_check_rule_fails() -> None:
    llm = _MockLLM(passed=False, reason="Not a greeting")
    rule = AICheckRule(rule_id="test.fail", prompt="Is this a greeting?", llm=llm)
    findings = rule.check(_make_doc("Goodbye"))
    assert len(findings) == 1
    assert findings[0].rule_id == "test.fail"
    assert findings[0].message == "Not a greeting"


def test_ai_check_rule_no_llm_raises() -> None:
    rule = AICheckRule(rule_id="test.no_llm", prompt="Check something.", llm=None)
    with pytest.raises(RuntimeError, match="requires an LLM client"):
        rule.check(_make_doc())


def test_ai_check_rule_from_config() -> None:
    llm = _MockLLM(passed=True)
    cfg: dict[str, Any] = {
        "id": "test.cfg",
        "type": "ai_check",
        "prompt": "Is it good?",
        "severity": "warning",
    }
    rule = AICheckRule.from_config(cfg, llm=llm)
    assert rule.id == "test.cfg"
    assert rule.severity == "warning"
    assert rule.prompt == "Is it good?"


def test_ai_check_rule_default_severity() -> None:
    rule = AICheckRule.from_config({"id": "r", "type": "ai_check", "prompt": "p"})
    assert rule.severity == "error"


# ---------------------------------------------------------------------------
# LLMClient protocol
# ---------------------------------------------------------------------------

def test_llm_client_protocol_satisfied() -> None:
    llm = _MockLLM()
    assert isinstance(llm, LLMClient)


def test_llm_client_protocol_not_satisfied() -> None:
    assert not isinstance(object(), LLMClient)


# ---------------------------------------------------------------------------
# RuleLoader with ai_check
# ---------------------------------------------------------------------------

def test_loader_ai_check_from_dicts() -> None:
    llm = _MockLLM(passed=True)
    rules = RuleLoader(llm=llm).load(
        [{"id": "ai.tone", "type": "ai_check", "prompt": "Is the tone professional?"}],
    )
    assert len(rules) == 1
    assert isinstance(rules[0], AICheckRule)


def test_loader_ai_check_no_llm_rule_raises_on_check() -> None:
    """Loading works fine; the error surfaces only when check() is called."""
    rules = RuleLoader(llm=None).load(
        [{"id": "ai.tone", "type": "ai_check", "prompt": "Is the tone professional?"}],
    )
    assert len(rules) == 1
    with pytest.raises(RuntimeError, match="requires an LLM client"):
        rules[0].check(_make_doc())


def test_loader_mixed_rules() -> None:
    llm = _MockLLM(passed=True)
    rules = RuleLoader(llm=llm).load(
        [
            {"id": "r.section", "type": "required_section", "match": "Introduction"},
            {"id": "r.ai", "type": "ai_check", "prompt": "Is this professional?"},
        ],
    )
    assert len(rules) == 2


# ---------------------------------------------------------------------------
# Provider import errors
# ---------------------------------------------------------------------------

def test_anthropic_client_import_error() -> None:
    with patch.dict(sys.modules, {"anthropic": None}), pytest.raises(ImportError, match="docchex\\[anthropic\\]"):
        AnthropicClient()


def test_openai_client_import_error() -> None:
    with patch.dict(sys.modules, {"openai": None}), pytest.raises(ImportError, match="docchex\\[openai\\]"):
        OpenAIClient()


def test_ollama_client_import_error_propagates() -> None:
    with patch.dict(sys.modules, {"openai": None}), pytest.raises(ImportError, match="docchex\\[openai\\]"):
        OllamaClient()


# ---------------------------------------------------------------------------
# OllamaClient delegation
# ---------------------------------------------------------------------------

def test_ollama_client_delegates_to_openai() -> None:
    mock_inner = MagicMock()
    mock_inner.evaluate.return_value = LLMResponse(passed=True, reason="delegated")

    # OllamaClient lazily imports OpenAIClient from providers.openai — patch it there.
    with patch(
        "docchex._internal.llm.providers.openai.OpenAIClient",
        return_value=mock_inner,
    ):
        client = OllamaClient(model="mistral")
        result = client.evaluate(_make_doc(), "check it")

    assert result.passed is True
    assert result.reason == "delegated"
    mock_inner.evaluate.assert_called_once()


# ---------------------------------------------------------------------------
# Integration: run_qaqc with ai_check
# ---------------------------------------------------------------------------

def test_run_qaqc_with_ai_check(tmp_path: Path) -> None:
    doc_file = tmp_path / "doc.txt"
    doc_file.write_text("This is a professional report.", encoding="utf-8")

    llm = _MockLLM(passed=True, reason="")
    result = run_qaqc(
        doc_file,
        [{"id": "ai.professional", "type": "ai_check", "prompt": "Is it professional?"}],
        llm=llm,
    )
    assert result["passed"] is True
    assert result["findings"] == []


def test_run_qaqc_with_ai_check_failure(tmp_path: Path) -> None:
    doc_file = tmp_path / "doc.txt"
    doc_file.write_text("lol yolo whatever", encoding="utf-8")

    llm = _MockLLM(passed=False, reason="Unprofessional tone")
    result = run_qaqc(
        doc_file,
        [{"id": "ai.professional", "type": "ai_check", "prompt": "Is it professional?"}],
        llm=llm,
    )
    assert result["passed"] is False
    assert len(result["findings"]) == 1
    assert result["findings"][0]["message"] == "Unprofessional tone"
