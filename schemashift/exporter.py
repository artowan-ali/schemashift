"""Export SchemaDiff results to various file formats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from schemashift.formatter import to_json, to_markdown
from schemashift.models import SchemaDiff


def export_diff(
    diff: SchemaDiff,
    output_path: Union[str, Path],
    fmt: str = "json",
) -> Path:
    """Write a formatted diff to *output_path*.

    Parameters
    ----------
    diff:
        The diff to export.
    output_path:
        Destination file path.  Parent directories are created automatically.
    fmt:
        Output format – ``"json"`` or ``"markdown"``.

    Returns
    -------
    Path
        The resolved path that was written.

    Raises
    ------
    ValueError
        If *fmt* is not a recognised format.
    """
    fmt = fmt.lower()
    if fmt not in ("json", "markdown", "md"):
        raise ValueError(f"Unsupported export format: {fmt!r}. Use 'json' or 'markdown'.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        content = to_json(diff)
    else:
        content = to_markdown(diff)

    output_path.write_text(content, encoding="utf-8")
    return output_path


def export_summary_json(diff: SchemaDiff, output_path: Union[str, Path]) -> Path:
    """Write a compact summary JSON (counts only) to *output_path*."""
    from schemashift.summarizer import summarize

    summary = summarize(diff)
    data = {
        "total": summary.total,
        "breaking": summary.breaking,
        "non_breaking": summary.non_breaking,
        "has_breaking_changes": summary.has_breaking_changes(),
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return output_path
