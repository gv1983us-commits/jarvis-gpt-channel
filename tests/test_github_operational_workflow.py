from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "GITHUB_OPERATIONAL_WORKFLOW.json"
SCHEMA_PATH = ROOT / "schemas" / "github-operation-receipt.schema.json"
REPORT_PATH = ROOT / "reports" / "2026-08-04-current-environment-capabilities.json"
DOC_PATH = ROOT / "GITHUB_OPERATIONAL_WORKFLOW.md"
AGENTS_PATH = ROOT / "AGENTS.md"

EXPECTED_MAIN_CHAIN = [
    "intake",
    "capability-probed",
    "repository-selected",
    "authority-checked",
    "source-pinned",
    "branch-created",
    "change-applied",
    "checks-completed",
    "receipt-prepared",
    "pull-request-opened",
    "review-resolved",
    "merge-authorized",
    "merged",
    "post-merge-verified",
    "handoff-recorded",
    "closed",
]


class GitHubOperationalWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")
        cls.agents = AGENTS_PATH.read_text(encoding="utf-8")

    def test_main_chain_is_complete_and_ordered(self) -> None:
        transitions = self.workflow["transitions"]
        pairs = [(item["from"], item["to"]) for item in transitions]
        expected_pairs = list(zip(EXPECTED_MAIN_CHAIN, EXPECTED_MAIN_CHAIN[1:]))
        self.assertEqual(pairs, expected_pairs)
        self.assertEqual(len(transitions), 15)
        self.assertEqual(len(self.workflow["states"]), 18)
        self.assertEqual(len(set(self.workflow["states"])), 18)

    def test_every_transition_is_bounded_and_evidenced(self) -> None:
        states = set(self.workflow["states"])
        for transition in self.workflow["transitions"]:
            with self.subTest(transition=transition):
                self.assertIn(transition["from"], states)
                self.assertIn(transition["to"], states)
                self.assertTrue(transition["requires"])
        self.assertIn("blocked", states)
        self.assertIn("aborted", states)
        self.assertGreaterEqual(len(self.workflow["stop_rules"]), 7)

    def test_authority_review_merge_and_post_merge_are_separate(self) -> None:
        boundary = self.workflow["authority_boundary"]
        self.assertFalse(boundary["grants_permissions"])
        self.assertFalse(boundary["creates_authority"])
        self.assertFalse(boundary["direct_default_branch_write"])
        self.assertEqual(boundary["default_write_mode"], "branch-and-draft-pull-request")
        merge = self.workflow["review_and_merge"]
        for marker in (
            "exact-head-sha",
            "required-checks-success",
            "no-required-unresolved-review",
            "task-specific-merge-authority",
        ):
            self.assertIn(marker, merge["merge_requires"])
        self.assertIn("read-default-branch", merge["post_merge_requires"])

    def test_bec_cdts_and_pca_handoffs_are_explicit(self) -> None:
        bec = self.workflow["bec_receipt"]
        self.assertEqual(bec["claim_domain"], "execution-evidence")
        for field in ("invocation", "observed_result", "evidence", "trust_anchor", "limitations"):
            self.assertIn(field, bec["required_fields"])
        cdts = self.workflow["cdts_handoff"]
        self.assertEqual(cdts["claim_domain"], "cross-domain-correlation")
        self.assertIn("merge_commit", cdts["required_links"])
        self.assertIn("world-truth", cdts["forbidden_inferences"])
        pca = self.workflow["pca_handoff"]
        self.assertEqual(pca["claim_domain"], "process-continuation")
        self.assertEqual(pca["applicability_values"], ["applicable", "not_applicable", "unknown"])

    def test_receipt_schema_tracks_workflow_states_and_safe_write_mode(self) -> None:
        enum = self.schema["properties"]["state"]["enum"]
        self.assertEqual(enum, self.workflow["states"])
        strategy = self.schema["properties"]["authority"]["properties"]["write_strategy"]
        self.assertEqual(strategy["const"], "branch-and-draft-pull-request")
        revision = self.schema["properties"]["source_pin"]["properties"]["base_revision"]
        self.assertEqual(revision["pattern"], "^[0-9a-f]{40}$")

    def test_capability_report_does_not_invent_a_hard_limit(self) -> None:
        limits = self.report["limits"]
        global_limit = limits["global_tool_calls_per_turn"]
        self.assertEqual(global_limit["status"], "unknown")
        self.assertIsNone(global_limit["exposed_value"])
        self.assertGreaterEqual(global_limit["observed_lower_bound"], 18)
        self.assertEqual(limits["assistant_tool_round_trips"]["hard_maximum"], "unknown")
        self.assertIn("Не преобразовывать", limits["rule"])

    def test_current_environment_is_connector_first(self) -> None:
        github = self.report["github"]
        self.assertTrue(github["permissions"]["push"])
        self.assertTrue(github["permissions"]["admin"])
        self.assertIn("read-actions-logs", github["verified_capabilities"])
        local = self.report["local_container"]
        for missing in ("gh", "docker", "ssh", "github.com DNS resolution"):
            self.assertIn(missing, local["unavailable"])
        self.assertIn("connector-first", local["conclusion"])

    def test_machine_entry_points_to_operational_workflow(self) -> None:
        self.assertIn("GITHUB_OPERATIONAL_WORKFLOW.json", self.agents)
        self.assertIn("GITHUB_OPERATIONAL_WORKFLOW.md", self.agents)
        for marker in (
            "задача",
            "проверка текущей формы и среды",
            "BEC receipt",
            "CDTS / PCA handoff",
            "expected head SHA",
        ):
            self.assertIn(marker, self.doc)
        self.assertTrue(WORKFLOW_PATH.read_text(encoding="utf-8").endswith("\n"))
        self.assertTrue(SCHEMA_PATH.read_text(encoding="utf-8").endswith("\n"))
        self.assertTrue(REPORT_PATH.read_text(encoding="utf-8").endswith("\n"))


if __name__ == "__main__":
    unittest.main()
