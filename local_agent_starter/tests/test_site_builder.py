from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.site_builder import create_site_project


class SiteBuilderTests(unittest.TestCase):
    def test_create_site_project_writes_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            output_root = workspace / "artifacts" / "sites"
            result = create_site_project(
                workspace=workspace,
                output_root=output_root,
                project_name="demo-site",
                title="Demo Site",
                brief="Pagina inicial para apresentar servicos.",
            )

            self.assertTrue(result["ok"])
            self.assertTrue((output_root / "demo-site" / "index.html").exists())
            self.assertTrue((output_root / "demo-site" / "styles.css").exists())
            self.assertTrue((output_root / "demo-site" / "script.js").exists())


if __name__ == "__main__":
    unittest.main()
