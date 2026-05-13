from __future__ import annotations

import json
from pathlib import Path
from typing import Any


Snapshot = dict[str, dict[str, int]]


def build_snapshot(workspace: Path, ignored_names: tuple[str, ...]) -> Snapshot:
    snapshot: Snapshot = {}
    ignored = set(ignored_names)
    for item in workspace.rglob("*"):
        if item.is_dir():
            continue
        relative = item.relative_to(workspace)
        if any(part in ignored for part in relative.parts):
            continue
        stat = item.stat()
        snapshot[str(relative).replace("\\", "/")] = {
            "size": int(stat.st_size),
            "mtime_ns": int(stat.st_mtime_ns),
        }
    return snapshot


def load_snapshot(snapshot_path: Path) -> Snapshot:
    if not snapshot_path.exists():
        return {}
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return {str(key): {"size": int(value["size"]), "mtime_ns": int(value["mtime_ns"])} for key, value in payload.items()}


def save_snapshot(snapshot_path: Path, snapshot: Snapshot) -> None:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def diff_snapshots(previous: Snapshot, current: Snapshot) -> dict[str, Any]:
    previous_paths = set(previous)
    current_paths = set(current)

    created = sorted(current_paths - previous_paths)
    deleted = sorted(previous_paths - current_paths)
    changed = sorted(path for path in (current_paths & previous_paths) if previous[path] != current[path])

    return {
        "created": created[:200],
        "changed": changed[:200],
        "deleted": deleted[:200],
        "summary": {
            "created_count": len(created),
            "changed_count": len(changed),
            "deleted_count": len(deleted),
        },
    }


class WorkspaceMonitor:
    def __init__(self, workspace: Path, snapshot_path: Path, ignored_names: tuple[str, ...]) -> None:
        self.workspace = workspace
        self.snapshot_path = snapshot_path
        self.ignored_names = ignored_names

    def scan(self, reset: bool = False) -> dict[str, Any]:
        current = build_snapshot(self.workspace, self.ignored_names)
        previous = {} if reset else load_snapshot(self.snapshot_path)
        save_snapshot(self.snapshot_path, current)

        if not previous:
            return {
                "ok": True,
                "baseline_created": True,
                "summary": {
                    "files_tracked": len(current),
                    "created_count": 0,
                    "changed_count": 0,
                    "deleted_count": 0,
                },
            }

        diff = diff_snapshots(previous, current)
        diff["ok"] = True
        diff["baseline_created"] = False
        diff["summary"]["files_tracked"] = len(current)
        return diff
