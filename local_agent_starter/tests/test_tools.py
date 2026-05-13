from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.config import Settings
from app.tools import ToolRegistry


class ToolRegistryTests(unittest.TestCase):
    def test_write_read_and_search_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            settings = Settings(
                model="qwen3:8b",
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                multimodal_base_url="https://api.openai.com/v1",
                multimodal_api_key="",
                transcription_model="gpt-4o-mini-transcribe",
                image_model="gpt-image-1",
                image_quality="medium",
                image_size="1024x1024",
                memory_db=workspace / "data" / "memory.sqlite3",
                workspace=workspace,
                artifacts_dir=workspace / "artifacts",
                site_output_dir=workspace / "artifacts" / "sites",
                image_output_dir=workspace / "artifacts" / "images",
                audio_output_dir=workspace / "artifacts" / "audio",
                monitor_snapshot_file=workspace / "data" / "snapshot.json",
                max_memory_messages=10,
                allow_write=True,
                enable_shell=False,
                shell_timeout_seconds=10,
                http_timeout_seconds=10,
                default_record_seconds=3,
                tts_rate=185,
                tts_voice_hint="",
                shell_allow_prefixes=("Get-ChildItem",),
                monitor_ignore_names=(".git", "__pycache__"),
            )

            tools = ToolRegistry(settings)
            tools.write_file("docs/example.txt", "linha importante")

            read_result = tools.read_file("docs/example.txt")
            search_result = tools.search_files("importante")

            self.assertTrue(read_result["ok"])
            self.assertIn("linha importante", read_result["content"])
            self.assertTrue(search_result["ok"])
            self.assertEqual(search_result["matches"][0]["path"], "docs/example.txt")


if __name__ == "__main__":
    unittest.main()
