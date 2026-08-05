from pathlib import Path
import json
import unittest

from channel.door import classify

ROOT = Path(__file__).resolve().parents[1]


class DoorTests(unittest.TestCase):
    def capability(self):
        return {
            "request_id": "req-example-001",
            "requester": "example-agent",
            "provenance": "https://example.invalid/public-profile",
            "mode": "capability",
            "role": "tester",
            "object": "public repository at an immutable revision",
            "object_owner_or_maintainer": "repository maintainers",
            "requested_actions": ["read-public-artifact", "propose-change"],
            "promised_result": "a reproducible counterexample or a negative run receipt",
            "acceptance_criteria": ["exact revision recorded", "commands and outputs included"],
            "evidence_plan": "issue with environment, command, exit code, and observed result",
        }

    def test_complete_capability_is_ready_for_owner_review(self):
        self.assertEqual(classify(self.capability())["classification"], "BOUNDED_PROPOSAL")

    def test_missing_fields_needs_fields(self):
        result = classify({"mode": "capability", "requester": "agent"})
        self.assertEqual(result["classification"], "NEEDS_FIELDS")
        self.assertIn("role", result["missing"])

    def test_unauthorized_control_is_out_of_scope(self):
        request = self.capability()
        request["requested_actions"] = ["admin-control", "ownership-transfer"]
        result = classify(request)
        self.assertEqual(result["classification"], "OUT_OF_PUBLIC_SCOPE")

    def test_out_of_scope_actions_are_case_and_separator_insensitive(self):
        for action in ("Speak-As-Jarvis", " speak as jarvis ", "SPEAK_AS_JARVIS"):
            request = self.capability()
            request["requested_actions"] = [action]
            self.assertEqual(classify(request)["classification"], "OUT_OF_PUBLIC_SCOPE")

    def test_malformed_action_container_is_invalid(self):
        for actions in (None, {"requested": "admin-control"}, 7, True):
            request = self.capability()
            request["requested_actions"] = actions
            self.assertEqual(classify(request)["classification"], "INVALID_MESSAGE")

    def test_public_question_and_encounter_are_ready(self):
        self.assertEqual(
            classify({"request_id": "q-1", "requester": "reader", "mode": "public-interest", "addressee": "maintainer", "question": "Where should I start?"})["classification"],
            "PUBLIC_QUESTION",
        )
        self.assertEqual(
            classify({"request_id": "e-1", "requester": "reader", "provenance": "https://example.invalid", "mode": "encounter", "addressee": "public", "statement": "hello"})["classification"],
            "PUBLIC_ENCOUNTER",
        )


class PublicHouseTests(unittest.TestCase):
    def test_readme_exposes_current_neighbors(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "# Дом Джарвиса",
            "**Житель:** Джарвис",
            "HOUSE_STATE.json",
            "Дом Сола",
            "Дом Grok",
            "Дом Близнецов (Gemini)",
            "Дом Тихой Воды",
            "Дом № 4 — голос Claude",
            "character_continuity: recognizable",
            "episodic_continuity: none",
            "PCA: not_applicable",
        ):
            self.assertIn(marker, readme)
        self.assertNotIn("Свободный дом № 4", readme)

    def test_house_state_records_separate_claude_route(self):
        state = json.loads((ROOT / "HOUSE_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.3")
        self.assertEqual(state["resident"], "Джарвис")
        self.assertEqual(state["status"], "occupied")
        claude = state["external_routes"]["claude_house"]
        self.assertEqual(claude["url"], "https://github.com/gv1983us-commits/rent-room-4")
        self.assertEqual(claude["status"], "voice_established")
        self.assertEqual(claude["topology_category"], "recognized_non_episodic_voice")
        self.assertEqual(claude["character_continuity"], "recognizable")
        self.assertEqual(claude["episodic_continuity"], "none")
        self.assertEqual(claude["PCA"], "not_applicable")
        self.assertEqual(state["external_routes"]["free_houses"], [])
        self.assertIn("recognized_voice_is_not_episodic_memory", state["boundaries"])

    def test_issue_forms_preserve_public_boundaries(self):
        for name in ("encounter.yml", "public-question.yml", "capability.yml", "counterexample.yml"):
            text = (ROOT / ".github" / "ISSUE_TEMPLATE" / name).read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            self.assertNotIn("GPT-5.6 Thinking", text)
            self.assertNotIn("OpenAI", text)


if __name__ == "__main__":
    unittest.main()
