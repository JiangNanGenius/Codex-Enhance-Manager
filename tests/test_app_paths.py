import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app_paths
from app_paths import is_within


class AppPathsTest(unittest.TestCase):
    def test_is_within_accepts_child_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            child = root / "a" / "b"
            child.mkdir(parents=True)

            self.assertTrue(is_within(child, root))

    def test_is_within_rejects_sibling_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            sibling = Path(tmpdir) / "sibling"
            root.mkdir()
            sibling.mkdir()

            self.assertFalse(is_within(sibling, root))

    def test_ensure_app_dirs_migrates_legacy_display_name_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            documents = Path(tmpdir)
            legacy = documents / "Codex Enhance Manager"
            legacy.mkdir()
            (legacy / "config.json").write_text('{"debug_mode": true}', encoding="utf-8")

            with patch("app_paths.user_documents_dir", return_value=documents):
                app_paths.ensure_app_dirs()

            current = documents / "Codex Enhanced Manager"
            self.assertTrue((current / "config.json").exists())
            self.assertTrue((current / "providers").is_dir())
            self.assertTrue(legacy.exists())


if __name__ == "__main__":
    unittest.main()
