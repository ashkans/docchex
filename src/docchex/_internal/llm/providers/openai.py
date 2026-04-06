from __future__ import annotations

__all__ = []

import json
from typing import TYPE_CHECKING

from docchex._internal.llm.base import LLMResponse

if TYPE_CHECKING:
    from docchex._internal.models import Document

_DEFAULT_MODEL = "gpt-4o-mini"
_SYSTEM_PROMPT = 'Respond only with JSON: {"passed": true, "reason": "..."}. Set passed to false if the document fails the check.'


class OpenAIClient:
    """LLM client backed by the OpenAI API (or any OpenAI-compatible endpoint).

    Requires ``pip install docchex[openai]``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        base_url: str | None = None,
    ) -> None:
        """Initialise the client.

        Parameters:
            api_key: OpenAI API key. Defaults to the ``OPENAI_API_KEY`` environment variable.
            model: Model ID to use for evaluation.
            base_url: Override the API base URL (e.g. for a local Ollama server).
        """
        try:
            import openai  # ty: ignore[unresolved-import]  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "openai package is required: pip install docchex[openai]",
            ) from exc
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def evaluate(self, doc: Document, prompt: str) -> LLMResponse:
        """Send the document and prompt to OpenAI and return a structured result."""
        text = doc.text[:32000]
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"{prompt}\n\nDocument:\n{text}"},
            ],
            max_tokens=256,
        )
        data = json.loads(response.choices[0].message.content)
        return LLMResponse(passed=bool(data["passed"]), reason=str(data.get("reason", "")))
