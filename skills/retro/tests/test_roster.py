import re, unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]  # .../skills
ROLES = ["pm", "sa", "dev", "qa", "sec", "tw"]

def frontmatter_name(p):
    text = p.read_text()
    m = re.search(r"^name:\s*(\S+)\s*$", text, re.M)
    return m.group(1) if m else None

class TestRoster(unittest.TestCase):
    def test_each_role_skill_exists_with_matching_name(self):
        for r in ROLES:
            sk = SKILLS / r / "SKILL.md"
            self.assertTrue(sk.is_file(), f"missing skill: {sk}")
            self.assertEqual(frontmatter_name(sk), r, f"frontmatter name mismatch in {sk}")

    def test_sdlc_orchestrator_delegates_to_every_role(self):
        sdlc = (SKILLS / "sdlc" / "SKILL.md").read_text()
        for r in ROLES:
            self.assertIn(f"gear:{r}", sdlc, f"sdlc must delegate to gear:{r}")

    def test_sdlc_keeps_the_six_phase_markers(self):
        sdlc = (SKILLS / "sdlc" / "SKILL.md").read_text()
        for n in range(6):
            self.assertIn(f"### Phase {n}", sdlc, f"sdlc must keep '### Phase {n}' marker")

    def test_tw_owns_md2docx_script(self):
        self.assertTrue((SKILLS / "tw" / "scripts" / "md2docx.py").is_file(),
                        "md2docx.py must move under skills/tw/scripts/")
        self.assertFalse((SKILLS / "sdlc" / "scripts" / "md2docx.py").is_file(),
                         "md2docx.py must no longer live under skills/sdlc/scripts/")

if __name__ == "__main__":
    unittest.main()
