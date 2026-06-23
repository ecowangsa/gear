import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]  # .../skills
RETRO = (SKILLS / "retro" / "SKILL.md").read_text()
SDLC = (SKILLS / "sdlc" / "SKILL.md").read_text()
COUNCIL = (SKILLS / "council" / "SKILL.md").read_text()


class TestSegitigaIntegration(unittest.TestCase):
    def test_retro_documents_handoff_mode(self):
        # retro (the hub) must accept material handed off by a sibling skill.
        self.assertIn("Handoff mode", RETRO)
        self.assertIn("primary candidate material", RETRO)
        self.assertIn("sdlc", RETRO)
        self.assertIn("council", RETRO)

    def test_sdlc_phase5_offers_retro_harvest(self):
        self.assertIn("/gear:retro", SDLC)
        self.assertIn("Harvest the lessons from this slice via retro", SDLC)
        self.assertIn("arc summary", SDLC)
        self.assertIn("Harvest is opt-in", SDLC)  # offer-first, not auto
        # the offer must live in/after Phase 5, not before it
        self.assertLess(
            SDLC.index("### Phase 5"),
            SDLC.index("/gear:retro"),
            "retro harvest offer must live in Phase 5",
        )

    def test_council_offers_retro_save_after_verdict(self):
        self.assertIn("/gear:retro", COUNCIL)
        self.assertIn("Save this decision as a lesson via retro", COUNCIL)
        self.assertIn("declin", COUNCIL.lower())  # offer-first: declining writes nothing
        # the save offer must come after the Chair synthesis (Step 5)
        self.assertLess(
            COUNCIL.index("## Step 5 - the Chair's synthesis"),
            COUNCIL.index("/gear:retro"),
            "save offer must come after the verdict",
        )

    def test_retro_frontmatter_is_strict_yaml_safe(self):
        # retro's description contains ": " which breaks a YAML *plain* scalar under
        # strict validation (frontmatter silently dropped). It must use a block scalar -
        # the same proven-safe pattern council already uses.
        frontmatter = RETRO.split("---", 2)[1]
        self.assertIn("description: |-", frontmatter)
        # content preserved through the conversion
        self.assertIn("harvest reusable lessons from the session", RETRO)


if __name__ == "__main__":
    unittest.main()
