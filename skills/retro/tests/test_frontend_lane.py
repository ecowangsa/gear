import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]

class TestFrontendLane(unittest.TestCase):
    def test_pm_offers_visual_companion_for_ui(self):
        pm = (SKILLS / "pm" / "SKILL.md").read_text().lower()
        self.assertIn("visual companion", pm)
        self.assertIn("ui-touching", pm)

    def test_dev_routes_frontend_design(self):
        dev = (SKILLS / "dev" / "SKILL.md").read_text()
        self.assertIn("frontend-design", dev)

    def test_sdlc_preflight_lists_frontend_design(self):
        sdlc = (SKILLS / "sdlc" / "SKILL.md").read_text()
        self.assertIn("frontend-design", sdlc)

if __name__ == "__main__":
    unittest.main()
