from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docchex._internal.llm.base import LLMResponse
    from docchex._internal.models import Document

_DEFAULT_MODEL = "llama3.2"
_DEFAULT_BASE_URL = "http://localhost:11434/v1"


class OllamaClient:
    """LLM client that connects to a local Ollama server via its OpenAI-compatible API.

    Requires ``pip install docchex[ollama]`` (installs the openai package).
    """

    def __init__(self, model: str = _DEFAULT_MODEL, base_url: str = _DEFAULT_BASE_URL) -> None:
        """Initialise the client.

        Parameters:
            model: Ollama model name (e.g. ``"llama3.2"``, ``"mistral"``).
            base_url: Base URL of the Ollama server.
        """
        from docchex._internal.llm.providers.openai import OpenAIClient  # noqa: PLC0415

        self._inner = OpenAIClient(api_key="ollama", model=model, base_url=base_url)

    def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
        """Send the document and prompt to Ollama and return a structured result."""
        return self._inner.evaluate(doc, prompt)
