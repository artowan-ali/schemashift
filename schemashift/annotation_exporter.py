"""Export annotated schema changes to JSON for downstream tooling."""

import json
from pathlib import Path
from typing import List

from schemashift.annotator import AnnotatedChange


def _annotated_to_dict(item: AnnotatedChange) -> dict:
    return {
        "table": item.change.table,
        "column": item.change.column,
        "change_type": item.change.change_type.value,
        "detail": item.change.detail,
        "breaking": item.is_breaking(),
        "severity": item.severity,
        "explanation": item.explanation,
        "suggestion": item.suggestion,
    }


def to_annotation_json(annotated: List[AnnotatedChange]) -> str:
    """Serialize annotated changes to a JSON string."""
    return json.dumps([_annotated_to_dict(a) for a in annotated], indent=2)


def export_annotations(annotated: List[AnnotatedChange], path: str) -> Path:
    """Write annotated changes as JSON to the given file path.

    Returns the resolved Path of the written file.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_annotation_json(annotated), encoding="utf-8")
    return output_path
