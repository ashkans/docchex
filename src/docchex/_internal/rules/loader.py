from __future__ import annotations

__all__ = []

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from docchex._internal.llm.base import LLMClient
    from docchex._internal.rules.base import Rule

_BUILTIN_RULE_TYPES: dict[str, type[Rule]] = {}

_RuleSource = str | Path | list[dict[str, Any]]


def _registry() -> dict[str, type[Rule]]:
    if not _BUILTIN_RULE_TYPES:
        from docchex._internal.rules.builtin.required_section import RequiredSectionRule  # noqa: PLC0415
        from docchex._internal.rules.builtin.word_count import WordCountRule  # noqa: PLC0415

        _BUILTIN_RULE_TYPES["required_section"] = RequiredSectionRule
        _BUILTIN_RULE_TYPES["word_count"] = WordCountRule
    return _BUILTIN_RULE_TYPES


class RuleLoader:
    def __init__(self, llm: LLMClient | None = None) -> None:
        """Initialise the loader.

        Parameters:
            llm: Optional LLM client injected into any ``ai_check`` rules that are loaded.
        """
        self._llm = llm

    def load(self, source: _RuleSource | list[_RuleSource]) -> list[Rule]:
        """Load rules from one or more sources.

        A single source can be:
        - A path string or Path to a ``.yaml``/``.yml``/``.toml`` file
        - A preset shorthand string like ``"preset:tech_report"``
        - A list of rule dicts

        Multiple sources can be combined by passing a list of any of the above.
        A list whose first element is not a dict is treated as a list of sources.
        """
        if isinstance(source, list) and (not source or not isinstance(source[0], dict)):
            rules: list[Rule] = []
            for s in source:
                rules.extend(self._load_single(s))  # ty: ignore[invalid-argument-type]
            return rules
        return self._load_single(source)  # ty: ignore[invalid-argument-type]

    def _load_single(self, source: _RuleSource) -> list[Rule]:
        if isinstance(source, list):
            return self._from_dicts(source)
        s = str(source)
        if s.startswith("preset:"):
            return self._from_preset(s[len("preset:"):])
        path = Path(source)
        if path.suffix in {".yaml", ".yml"}:
            return self._from_yaml(path)
        if path.suffix == ".toml":
            return self._from_toml(path)
        raise ValueError(f"Unsupported rule source: {source!r}")

    def _from_preset(self, name: str) -> list[Rule]:
        from docchex._internal.rules.presets import _resolve_preset  # noqa: PLC0415
        try:
            import yaml  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError("PyYAML is required to load presets: pip install pyyaml") from exc
        data = yaml.safe_load(_resolve_preset(name))
        return self._from_dicts(data.get("rules", []))

    def _from_yaml(self, path: Path) -> list[Rule]:
        try:
            import yaml  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError("PyYAML is required to load YAML rules: pip install pyyaml") from exc
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return self._from_dicts(data.get("rules", []))

    def _from_toml(self, path: Path) -> list[Rule]:
        try:
            import tomllib  # noqa: PLC0415
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]  # ty: ignore[unresolved-import]  # noqa: PLC0415
            except ImportError as exc:
                raise ImportError("tomli is required for Python < 3.11: pip install tomli") from exc
        with path.open("rb") as f:
            data = tomllib.load(f)
        return self._from_dicts(data.get("rules", []))

    def _from_dicts(self, rule_dicts: list[dict[str, Any]]) -> list[Rule]:
        registry = _registry()
        rules: list[Rule] = []
        for cfg in rule_dicts:
            rule_type = cfg.get("type")
            if rule_type == "ai_check":
                from docchex._internal.rules.builtin.ai_check import AICheckRule  # noqa: PLC0415

                rules.append(AICheckRule.from_config(cfg, llm=self._llm))
                continue
            if rule_type not in registry:
                raise ValueError(
                    f"Unknown rule type: {rule_type!r}. Available: {[*list(registry), 'ai_check']}",
                )
            rules.append(registry[rule_type].from_config(cfg))
        return rules
