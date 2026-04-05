from __future__ import annotations

__all__ = []

import importlib.resources

_PRESET_NAMES = frozenset({"tech_report", "academic_paper", "letter_email", "custom_template"})
_PACKAGE = "docchex._internal.rules.presets"


def _available_presets() -> list[str]:
    return sorted(_PRESET_NAMES)


def _resolve_preset(name: str) -> str:
    if name not in _PRESET_NAMES:
        raise ValueError(f"Unknown preset: {name!r}. Available: {sorted(_PRESET_NAMES)}")
    return importlib.resources.files(_PACKAGE).joinpath(f"{name}.yaml").read_text(encoding="utf-8")
