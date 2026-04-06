"""docchex — document QA/QC engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docchex._internal.cli import get_parser, main
from docchex._internal.evaluation.engine import RuleEngine
from docchex._internal.llm.base import LLMClient, LLMResponse
from docchex._internal.llm.providers.anthropic import AnthropicClient
from docchex._internal.llm.providers.ollama import OllamaClient
from docchex._internal.llm.providers.openai import OpenAIClient
from docchex._internal.models import Document, Finding, Report
from docchex._internal.parsing.base import DocumentParser
from docchex._internal.parsing.pdf import PDFParser
from docchex._internal.parsing.text import TextParser
from docchex._internal.rules.base import Rule, Severity
from docchex._internal.rules.builtin.ai_check import AICheckRule
from docchex._internal.rules.builtin.required_section import RequiredSectionRule
from docchex._internal.rules.builtin.word_count import WordCountRule
from docchex._internal.rules.loader import RuleLoader
from docchex._internal.rules.presets import _available_presets

_RulesArg = str | Path | list[dict[str, Any]] | list[str | Path | list[dict[str, Any]]]


def list_presets() -> list[str]:
    """Return the names of all built-in rule presets.

    Returns:
        A sorted list of preset names.
        Pass any name as ``"preset:<name>"`` to ``run_qaqc`` or ``RuleLoader.load``.

    Example:
        ```python
        docchex.list_presets()
        # ['academic_paper', 'custom_template', 'letter_email', 'tech_report']

        run_qaqc("report.pdf", "preset:tech_report")
        run_qaqc("report.pdf", ["preset:tech_report", "my_extra_rules.yaml"])
        ```
    """
    return _available_presets()


def run_qaqc(
    document: str | Path,
    rules: _RulesArg,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    """Run QA/QC checks on a document against a set of rules.

    Parameters:
        document: Path to the document file (PDF or TXT supported).
        rules: One or more rule sources. Can be:
            - A path string or ``Path`` to a ``.yaml``/``.toml`` rules file
            - A preset name like ``"preset:tech_report"`` (see ``list_presets()``)
            - A list of rule dicts (including ``type: ai_check`` entries)
            - A list combining any of the above
        llm: Optional LLM client for ``ai_check`` rules (e.g. ``AnthropicClient()``).

    Returns:
        A dict with keys: ``document``, ``passed``, ``summary``, ``findings``.
    """
    doc_path = Path(document)
    parsed_doc = DocumentParser.for_path(doc_path).parse(doc_path)
    loaded_rules = RuleLoader(llm=llm).load(rules)
    report = RuleEngine(loaded_rules).run(parsed_doc)
    return report.to_dict()


__all__ = [
    "AICheckRule",
    "AnthropicClient",
    "Document",
    "DocumentParser",
    "Finding",
    "LLMClient",
    "LLMResponse",
    "OllamaClient",
    "OpenAIClient",
    "PDFParser",
    "Report",
    "RequiredSectionRule",
    "Rule",
    "RuleEngine",
    "RuleLoader",
    "Severity",
    "TextParser",
    "WordCountRule",
    "get_parser",
    "list_presets",
    "main",
    "run_qaqc",
]
