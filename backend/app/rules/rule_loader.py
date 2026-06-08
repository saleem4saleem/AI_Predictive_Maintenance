from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.core.config import BACKEND_DIR

DEFAULT_RULES_PATH = BACKEND_DIR / "app" / "rules" / "maintenance_rules.yaml"


class RuleLoadError(RuntimeError):
    """Raised when the YAML rules file cannot be loaded safely."""


def load_rules(path: Path | None = None) -> list[dict[str, Any]]:
    rules_path = path or DEFAULT_RULES_PATH
    if not rules_path.exists():
        raise RuleLoadError(f"Rules file was not found at {rules_path}.")

    try:
        content = yaml.safe_load(rules_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise RuleLoadError("Rules file contains invalid YAML.") from exc
    except OSError as exc:
        raise RuleLoadError("Rules file could not be read.") from exc

    rules = content.get("rules", [])
    if not isinstance(rules, list):
        raise RuleLoadError("Rules file must contain a top-level 'rules' list.")
    return rules
