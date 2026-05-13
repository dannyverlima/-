from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.monitoring import WorkspaceMonitor


class WorkspaceMonitorTests(unittest.TestCase):
    def test_scan_reports_created_changed_and_deleted_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            snapshot = workspace / "data" / "snapshot.json"
            monitor = WorkspaceMonitor(workspace, snapshot, (".git", "__pycache__"))

            (workspace / "alpha.txt").write_text("one", encoding="utf-8")
            baseline = monitor.scan()
            self.assertTrue(baseline["baseline_created"])

            (workspace / "alpha.txt").write_text("two", encoding="utf-8")
            (workspace / "beta.txt").write_text("new", encoding="utf-8")
            diff = monitor.scan()

            self.assertIn("alpha.txt", diff["changed"])
            self.assertIn("beta.txt", diff["created"])

            (workspace / "beta.txt").unlink()
            deleted = monitor.scan()
            self.assertIn("beta.txt", deleted["deleted"])


if __name__ == "__main__":
    unittest.main()
