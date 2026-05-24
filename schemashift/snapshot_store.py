"""Manage a directory-based store of named snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from schemashift.snapshot import Snapshot, save_snapshot, load_snapshot


DEFAULT_STORE_DIR = Path(".schemashift/snapshots")


class SnapshotStore:
    """Persist and retrieve snapshots from a local directory."""

    def __init__(self, store_dir: Path = DEFAULT_STORE_DIR) -> None:
        self.store_dir = Path(store_dir)

    def _path_for(self, label: str) -> Path:
        safe_label = label.replace("/", "_").replace(" ", "_")
        return self.store_dir / f"{safe_label}.json"

    def save(self, snapshot: Snapshot) -> Path:
        """Persist a snapshot; returns the file path written."""
        path = self._path_for(snapshot.label)
        save_snapshot(snapshot, path)
        return path

    def load(self, label: str) -> Snapshot:
        """Load a snapshot by label. Raises FileNotFoundError if missing."""
        return load_snapshot(self._path_for(label))

    def exists(self, label: str) -> bool:
        """Return True if a snapshot with the given label exists."""
        return self._path_for(label).exists()

    def list_labels(self) -> List[str]:
        """Return all stored snapshot labels (sorted alphabetically)."""
        if not self.store_dir.exists():
            return []
        return sorted(
            p.stem for p in self.store_dir.iterdir() if p.suffix == ".json"
        )

    def delete(self, label: str) -> bool:
        """Delete a snapshot file. Returns True if deleted, False if not found."""
        path = self._path_for(label)
        if path.exists():
            path.unlink()
            return True
        return False

    def latest(self) -> Optional[Snapshot]:
        """Return the most recently modified snapshot, or None if store is empty."""
        if not self.store_dir.exists():
            return None
        files = sorted(
            (p for p in self.store_dir.iterdir() if p.suffix == ".json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not files:
            return None
        return load_snapshot(files[0])
