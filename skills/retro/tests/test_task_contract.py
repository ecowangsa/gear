import json, unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
REF = SKILLS / "sdlc" / "references"
SCHEMA = REF / "task-contract.schema.json"
EXAMPLE = REF / "task-contract.example.json"
REQUIRED = ["id", "goal", "inputs", "output_schema", "acceptance", "deps", "isolation", "verify"]

class TestTaskContract(unittest.TestCase):
    def test_schema_is_valid_json_with_required_fields(self):
        self.assertTrue(SCHEMA.is_file(), f"missing {SCHEMA}")
        s = json.loads(SCHEMA.read_text())
        self.assertEqual(set(s.get("required", [])), set(REQUIRED))
        for f in REQUIRED:
            self.assertIn(f, s.get("properties", {}), f"schema missing property {f}")
        self.assertEqual(s["properties"]["isolation"].get("enum"), ["none", "worktree"])

    def test_example_backlog_conforms(self):
        self.assertTrue(EXAMPLE.is_file(), f"missing {EXAMPLE}")
        units = json.loads(EXAMPLE.read_text())
        self.assertIsInstance(units, list)
        self.assertGreaterEqual(len(units), 2)
        ids = set()
        for u in units:
            for f in REQUIRED:
                self.assertIn(f, u, f"unit {u.get('id')} missing field {f}")
            self.assertIsInstance(u["id"], str)
            self.assertIsInstance(u["inputs"], list)
            self.assertIsInstance(u["acceptance"], list)
            self.assertIsInstance(u["deps"], list)
            self.assertIn(u["isolation"], ["none", "worktree"])
            self.assertIn("strategy", u["verify"])
            ids.add(u["id"])
        for u in units:
            for d in u["deps"]:
                self.assertIn(d, ids, f"unit {u['id']} dep {d} not a known unit id")

    def test_pm_emits_the_contract(self):
        pm = (SKILLS / "pm" / "SKILL.md").read_text()
        self.assertIn("task-contract", pm)
        self.assertIn("work unit", pm.lower())

    def test_sdlc_documents_multi_agent_execution(self):
        sdlc = (SKILLS / "sdlc" / "SKILL.md").read_text()
        self.assertIn("task-contract", sdlc)
        for anchor in ["worktree", "adversarial", "Workflow"]:
            self.assertIn(anchor, sdlc, f"sdlc multi-agent section missing '{anchor}'")

if __name__ == "__main__":
    unittest.main()
