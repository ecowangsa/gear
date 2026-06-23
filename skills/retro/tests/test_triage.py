import re, unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
TRIAGE = SKILLS / "triage" / "SKILL.md"

class TestTriage(unittest.TestCase):
    def test_skill_exists_with_matching_name(self):
        self.assertTrue(TRIAGE.is_file(), f"missing {TRIAGE}")
        m = re.search(r"^name:\s*(\S+)\s*$", TRIAGE.read_text(), re.M)
        self.assertIsNotNone(m, "no frontmatter name")
        self.assertEqual(m.group(1), "triage")

    def test_emits_task_contract_backlog(self):
        t = TRIAGE.read_text()
        self.assertIn("task-contract", t)
        for sev in ["P0", "P1", "P2", "P3"]:
            self.assertIn(sev, t, f"severity {sev} not documented")

    def test_offers_both_handoffs(self):
        t = TRIAGE.read_text()
        self.assertIn("/gear:retro", t)
        self.assertIn("/gear:sdlc", t)

    def test_documents_cycle_position(self):
        t = TRIAGE.read_text().lower()
        self.assertIn("council", t)
        self.assertIn("triage", t)

    def test_council_offers_triage_handoff(self):
        council = (SKILLS / "council" / "SKILL.md").read_text()
        self.assertIn("/gear:triage", council)

if __name__ == "__main__":
    unittest.main()
