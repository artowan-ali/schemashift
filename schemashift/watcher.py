"""File-based schema watcher: compare two schema files and export results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from schemashift.differ import diff_schemas
from schemashift.exporter import export_diff, export_summary_json
from schemashift.loader import load_schema_from_file
from schemashift.models import SchemaDiff
from schemashift.summarizer import summarize, DiffSummary


@dataclass
class WatchResult:
    """Outcome of a single schema comparison run."""

    diff: SchemaDiff
    summary: DiffSummary
    exported_paths: list[Path] = field(default_factory=list)

    @property
    def has_breaking_changes(self) -> bool:
        return self.summary.has_breaking_changes()


def watch(
    before_path: str | Path,
    after_path: str | Path,
    *,
    export_dir: Optional[str | Path] = None,
    fmt: str = "json",
    export_summary: bool = False,
) -> WatchResult:
    """Compare two schema files and optionally export the results.

    Parameters
    ----------
    before_path:
        Path to the *before* SQL schema file.
    after_path:
        Path to the *after* SQL schema file.
    export_dir:
        Directory to write output files into.  When *None* nothing is written.
    fmt:
        Export format for the diff file (``"json"`` or ``"markdown"``).  Only
        used when *export_dir* is set.
    export_summary:
        When *True* also write a compact summary JSON alongside the diff file.

    Returns
    -------
    WatchResult
    """
    before = load_schema_from_file(before_path)
    after = load_schema_from_file(after_path)
    diff = diff_schemas(before, after)
    summary = summarize(diff)
    exported: list[Path] = []

    if export_dir is not None:
        export_dir = Path(export_dir)
        ext = "md" if fmt.lower() in ("markdown", "md") else "json"
        diff_path = export_dir / f"diff.{ext}"
        exported.append(export_diff(diff, diff_path, fmt=fmt))

        if export_summary:
            summary_path = export_dir / "summary.json"
            exported.append(export_summary_json(diff, summary_path))

    return WatchResult(diff=diff, summary=summary, exported_paths=exported)
