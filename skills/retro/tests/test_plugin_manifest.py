import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # repo root
MANIFEST = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())


class TestPluginManifest(unittest.TestCase):
    def test_no_redundant_standard_hooks_declaration(self):
        # Claude Code auto-loads the standard hooks/hooks.json. Declaring it again in
        # manifest.hooks double-loads and breaks plugin load ("Duplicate hooks file").
        # manifest.hooks must only reference ADDITIONAL hook files - so for gear,
        # whose only hook file is the standard one, it must be absent.
        self.assertNotIn(
            "hooks", MANIFEST,
            "plugin.json must not declare the standard hooks/hooks.json (it auto-loads)",
        )

    def test_standard_hooks_file_exists(self):
        self.assertTrue(
            (ROOT / "hooks" / "hooks.json").is_file(),
            "the standard hooks/hooks.json must exist so hooks auto-load",
        )


if __name__ == "__main__":
    unittest.main()
