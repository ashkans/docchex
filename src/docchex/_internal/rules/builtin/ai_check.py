from __future__ import annotations

__all__ = []

from typing import TYPE_CHECKING, Any

from docchex._internal.rules.base import Rule, Severity

if TYPE_CHECKING:
    from docchex._internal.llm.base import LLMClient
    from docchex._internal.models import Document, Finding


class AICheckRule(Rule):
    """Checks a document against a custom prompt using an LLM.

    The LLM is expected to return JSON with ``{"passed": bool, "reason": str}``.
    If the document fails the check, a finding is emitted with the reason as the message.
    """

    id: str
    """Rule identifier."""
    prompt: str
    """The evaluation prompt sent to the LLM together with the document text."""
    severity: str
    """Severity of findings produced when the document fails the check."""

    def __init__(
        self,
        rule_id: str,
        prompt: str,
        severity: str = Severity.ERROR,
        llm: LLMClient | None = None,
    ) -> None:
        self.id = rule_id
        self.prompt = prompt
        self.severity = severity
        self._llm = llm

    def check(self, doc: Document) -> list[Finding]:
        """Evaluate the document using the configured LLM and return any findings.

        Raises:
            RuntimeError: If no LLM client was provided.
        """
        if self._llm is None:
            raise RuntimeError(
                f"Rule {self.id!r} requires an LLM client. "
                "Pass llm=... to RuleLoader or AICheckRule.",
            )
        from docchex._internal.models import Finding  # noqa: PLC0415

        result = self._llm.evaluate(doc, self.prompt)
        if result.passed:
            return []
        return [Finding(rule_id=self.id, severity=self.severity, message=result.reason)]

    @classmethod
    def from_config(
        cls,
        config: dict[str, Any],
        llm: LLMClient | None = None,
    ) -> AICheckRule:
        """Instantiate from a rule configuration dictionary.

        Parameters:
            config: Rule config dict with keys ``id``, ``prompt``, and optional ``severity``.
            llm: LLM client to use for evaluation.
        """
        return cls(
            rule_id=config["id"],
            prompt=config["prompt"],
            severity=config.get("severity", Severity.ERROR),
            llm=llm,
        )
