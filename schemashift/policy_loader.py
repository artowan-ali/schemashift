"""Load policy rules from a YAML or dict configuration."""

from typing import Any, Dict, List
from schemashift.models import ChangeType
from schemashift.policy import PolicyRule


_CHANGE_TYPE_MAP: Dict[str, ChangeType] = {
    "column_removed": ChangeType.COLUMN_REMOVED,
    "column_added": ChangeType.COLUMN_ADDED,
    "column_type_changed": ChangeType.COLUMN_TYPE_CHANGED,
    "table_removed": ChangeType.TABLE_REMOVED,
    "table_added": ChangeType.TABLE_ADDED,
    "nullable_changed": ChangeType.NULLABLE_CHANGED,
}


def _parse_change_types(raw: List[str]) -> List[ChangeType]:
    result = []
    for name in raw:
        ct = _CHANGE_TYPE_MAP.get(name.lower())
        if ct is None:
            raise ValueError(f"Unknown change type in policy: '{name}'")
        result.append(ct)
    return result


def load_policy_from_dict(config: Dict[str, Any]) -> List[PolicyRule]:
    """Parse a list of PolicyRule objects from a config dict."""
    rules = []
    for entry in config.get("rules", []):
        name = entry.get("name", "unnamed")
        message = entry.get("message", "Change blocked by policy")
        blocked_types = _parse_change_types(entry.get("blocked_change_types", []))
        blocked_tables = entry.get("blocked_tables", [])
        rules.append(PolicyRule(
            name=name,
            blocked_change_types=blocked_types,
            blocked_tables=blocked_tables,
            message=message,
        ))
    return rules


def load_policy_from_yaml(path: str) -> List[PolicyRule]:
    """Load policy rules from a YAML file."""
    try:
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML is required to load policy from YAML files.") from e

    with open(path, "r") as f:
        config = yaml.safe_load(f) or {}
    return load_policy_from_dict(config)
