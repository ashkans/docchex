from __future__ import annotations

__all__ = []

import json
from typing import TYPE_CHECKING

from docchex._internal.llm.base import LLMResponse

if TYPE_CHECKING:
    from docchex._internal.models import Document

_DEFAULT_MODEL = "claude-3-5-haiku-20241022"
_SYSTEM_PROMPT = 'Respond only with JSON: {"passed": true, "reason": "..."}. Set passed to false if the document fails the check.'


class AnthropicClient:
    """LLM client backed by the Anthropic API.

    Requires ``pip install docchex[anthropic]``.
    """

    def __init__(self, api_key: str | None = None, model: str = _DEFAULT_MODEL) -> None:
        """Initialise the client.

        Parameters:
            api_key: Anthropic API key. Defaults to the ``ANTHROPIC_API_KEY`` environment variable.
            model: Model ID to use for evaluation.
        """
        try:
            import anthropic  # ty: ignore[unresolved-import]  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required: pip install docchex[anthropic]",
            ) from exc
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
        """Send the document and prompt to Anthropic and return a structured result."""
        text = doc.text[:32000]
        message = self._client.messages.create(
            model=self._model,
            max_tokens=256,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"}],
        )
        data = json.loads(message.content[0].text)
        return LLMResponse(passed=bool(data["passed"]), reason=str(data.get("reason", "")))
