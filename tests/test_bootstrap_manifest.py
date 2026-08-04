import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "AGENT_BOOTSTRAP_MANIFEST.json"

EXPECTED_REVISIONS = {
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
        cls.raw = MANIFEST_PATH.read_text(encoding="utf-8")
        cls.manifest = json.loads(cls.raw)

    def test_manifest_is_utf8_json_with_terminal_newline(self):
        self.assertTrue(self.raw.endswith("\n"))
        self.assertEqual(self.manifest["schema_version"], "0.1.0")
        self.assertEqual(self.manifest["status"], "public-draft")
        self.assertEqual(self.manifest["language"], "ru")

    def test_manifest_preserves_navigation_only_boundary(self):
        boundary = self.manifest["authority_boundary"]
        self.assertEqual(boundary["kind"], "navigation-only")
        self.assertFalse(boundary["normative_union"])
        self.assertFalse(boundary["imports_external_verdicts"])
        self.assertFalse(boundary["grants_permissions"])
        self.assertFalse(boundary["establishes_identity"])
        self.assertFalse(boundary["establishes_world_truth"])

    def test_host_pairs_machine_and_human_entries_at_one_commit(self):
        host = self.manifest["host"]
        self.assertEqual(host["repository"], "gv1983us-commits/jarvis-gpt-channel")
        self.assertEqual(host["manifest_path"], "AGENT_BOOTSTRAP_MANIFEST.json")
        self.assertEqual(host["human_entry_path"], "AGENT_ZERO_POINT.md")
        self.assertIn("одного и того же commit SHA", host["ref_policy"])

    def test_component_ids_and_revisions_are_explicit_and_pinned(self):
        components = self.manifest["components"]
        by_id = {component["id"]: component for component in components}
        self.assertEqual(len(components), len(by_id))
        self.assertEqual(set(by_id), set(EXPECTED_REVISIONS))
        self.assertEqual(self.manifest["integrity"]["source_count"], len(components))
        self.assertTrue(self.manifest["integrity"]["all_external_components_pinned"])

        for component_id, expected_revision in EXPECTED_REVISIONS.items():
            component = by_id[component_id]
            with self.subTest(component=component_id):
                self.assertEqual(component["pinned_revision"], expected_revision)
                self.assertRegex(component["pinned_revision"], re.compile(r"^[0-9a-f]{40}$"))
                self.assertEqual(component["default_branch"], "main")
                self.assertTrue(component["repository"].startswith("gv1983us-commits/"))
                self.assertTrue(component["required_paths"])
                self.assertTrue(component["validation_commands"])

    def test_routes_reference_only_declared_components(self):
        component_ids = {component["id"] for component in self.manifest["components"]}
        for route_name, route in self.manifest["routes"].items():
            for component_id in route["components"]:
                with self.subTest(route=route_name, component=component_id):
                    self.assertIn(component_id, component_ids)

    def test_capability_checks_are_voluntary_non_exam_and_environment_scoped(self):
        checks = self.manifest["capability_checks"]
        self.assertEqual(checks["participation"], "voluntary")
        self.assertFalse(checks["is_exam"])
        self.assertFalse(checks["is_admission_gate"])
        self.assertIn("именно этой формы", checks["purpose"])
        self.assertIn("именно этой среде", checks["purpose"])
        self.assertIn("model + runtime/host + platform", checks["scope_rule"])
        self.assertIn("not_checked", checks["recommended_record_states"])
        self.assertIn("unknown", checks["recommended_record_states"])
        self.assertIn("без экзаменационного балла", checks["recording_rule"])

        human_entry = (ROOT / "AGENT_ZERO_POINT.md").read_text(encoding="utf-8")
        for marker in (
            "## Добровольные проверки возможностей",
            "Это не экзамен",
            "текущих возможностей именно этой формы в именно этой среде",
            "Непройденная или невозможная проверка не считается провалом участника",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, human_entry)

    def test_runtime_and_receipt_contracts_have_required_surfaces(self):
        runtime_fields = set(self.manifest["runtime_checklist"]["required_fields"])
        self.assertTrue({
            "model",
            "runtime_or_host",
            "platform",
            "available_tools",
            "task_authorization",
            "invoked_tools",
            "evidence",
            "unknowns",
        }.issubset(runtime_fields))

        receipt_fields = set(self.manifest["output_contract"]["minimum_receipt_fields"])
        self.assertTrue({
            "repository",
            "base_revision",
            "result_revision",
            "paths_changed",
            "checks_run",
            "check_results",
        }.issubset(receipt_fields))

    def test_write_policy_defaults_to_branch_and_draft_pr(self):
        policy = self.manifest["write_policy"]
        self.assertEqual(policy["default_strategy"], "branch-and-draft-pull-request")
        self.assertFalse(policy["direct_default_branch_writes"])
        self.assertEqual(policy["destructive_actions"]["default"], "prohibited")
        self.assertTrue(policy["destructive_actions"]["require_explicit_human_authority"])
        self.assertFalse(policy["secrets"]["publish"])


if __name__ == "__main__":
    unittest.main()
