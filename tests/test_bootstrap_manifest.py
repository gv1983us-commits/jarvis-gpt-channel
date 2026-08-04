import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "arb": "6b6c32cd467a4b5e4863d082b9da5bdd40d7dced",
    "mpaa": "93593b86968d7a5217954a0937d6038298cb6f6f",
    "bec": "cb005442ad412b1309d8e96aba145c72773cae59",
    "pca": "c57493540da1590c9ccf43c1b330cae735e9040c",
    "cdts": "f91dbc003519efd5264655d905d0530dbfeac2fd",
    "review_protocol": "e2ff9182014d8a8f3c3e7ea1ea269eecb8679035",
}


class AgentBootstrapManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "AGENT_BOOTSTRAP_MANIFEST.json").read_text(encoding="utf-8"))

    def test_machine_host_and_disclosure_order(self):
        self.assertEqual(self.manifest["schema_version"], "0.2.0")
        boundary = self.manifest["authority_boundary"]
        self.assertEqual(boundary["kind"], "machine-navigation-only")
        self.assertFalse(boundary["human_public_surface_is_technical_source"])
        host = self.manifest["host"]
        self.assertEqual(host["machine_discovery_path"], "AGENTS.md")
        self.assertEqual(host["machine_entry_path"], "AGENT_ENTRY.md")
        self.assertEqual(host["reasoning_matrix_path"], "AGENT_ZERO_POINT.md")
        gate = self.manifest["disclosure_gate"]
        self.assertEqual(gate["sequence"], ["know", "understand", "verify", "disclose"])
        self.assertTrue(gate["fail_closed"])

    def test_sources_are_pinned_and_routes_are_bounded(self):
        by_id = {item["id"]: item for item in self.manifest["components"]}
        self.assertEqual(set(by_id), set(EXPECTED))
        for component_id, revision in EXPECTED.items():
            item = by_id[component_id]
            self.assertEqual(item["pinned_revision"], revision)
            self.assertRegex(revision, re.compile(r"^[0-9a-f]{40}$"))
            self.assertTrue(item["required_paths"])
            self.assertTrue(item["validation_commands"])
        for route in self.manifest["routes"].values():
            self.assertTrue(set(route["components"]).issubset(by_id))

    def test_checks_are_voluntary_and_matrices_exist(self):
        checks = self.manifest["capability_checks"]
        self.assertEqual(checks["participation"], "voluntary")
        self.assertFalse(checks["is_exam"])
        self.assertFalse(checks["is_admission_gate"])
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        entry = (ROOT / "AGENT_ENTRY.md").read_text(encoding="utf-8")
        zero = (ROOT / "AGENT_ZERO_POINT.md").read_text(encoding="utf-8")
        for marker in ("знать", "понять", "проверить", "раскрыть форму"):
            self.assertIn(marker, agents)
        self.assertIn("## Матрица раскрытия", entry)
        self.assertIn("## Навигационная матрица", zero)
        self.assertIn("## Загрузочная матрица", zero)

    def test_write_policy_remains_bounded(self):
        policy = self.manifest["write_policy"]
        self.assertEqual(policy["default_strategy"], "branch-and-draft-pull-request")
        self.assertFalse(policy["direct_default_branch_writes"])
        self.assertEqual(policy["destructive_actions"]["default"], "prohibited")


if __name__ == "__main__":
    unittest.main()
