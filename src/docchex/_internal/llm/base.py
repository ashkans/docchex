from __future__ import annotations

__all__ = []

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from docchex._internal.models import Document


@dataclass
class LLMResponse:
    """Result returned by an LLM provider after evaluating a document."""

    passed: bool
    """Whether the document passed the check."""
    reason: str
    """Human-readable explanation of the result."""


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM providers used by :class:`~docchex.AICheckRule`.

    Any object that implements ``evaluate(doc, prompt) -> LLMResponse`` satisfies this
    protocol — no subclassing required.

    Built-in providers
    ------------------
    - :class:`~docchex.AnthropicClient` — Anthropic API (``pip install docchex[anthropic]``)
    - :class:`~docchex.OpenAIClient` — OpenAI API or any OpenAI-compatible endpoint
      (``pip install docchex[openai]``)
    - :class:`~docchex.OllamaClient` — local Ollama server via the OpenAI-compatible API
      (``pip install docchex[ollama]``)

    Custom providers
    ----------------
    Implement a custom provider by defining a class with the ``evaluate`` method::

        class MyClient:
            def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
                ...
                return LLMResponse(passed=True, reason="All good")

        loader = RuleLoader(llm=MyClient())

    Future extensibility
    --------------------
    The current design supports single-call, stateless checks: one prompt is sent to the
    LLM and a pass/fail result is returned. If multi-step reasoning becomes necessary
    (e.g. agent loops, tool calling, or structured-output retries), the natural approach
    is to implement a richer ``LLMClient`` that encapsulates that logic internally —
    the rest of the pipeline (``AICheckRule``, ``RuleLoader``, ``run_qaqc``) stays
    unchanged. For that use case, `litellm <https://docs.litellm.ai>`_ (lightweight,
    100+ providers) or `LangChain <https://python.langchain.com>`_ (full agent
    orchestration) are good building blocks to wrap inside a custom ``LLMClient``.
    """

    def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
        """Evaluate the document against the given prompt and return a structured result."""
        ...
