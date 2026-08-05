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
        self.assertEqual(
            classify(self.capability()),
            {
                "classification": "BOUNDED_PROPOSAL",
                "message_status": "READY_FOR_OWNER_REVIEW",
                "ownership_effect": "NONE",
            },
        )

    def test_missing_fields_needs_fields(self):
        result = classify({"mode": "capability", "requester": "agent"})
        self.assertEqual(result["classification"], "NEEDS_FIELDS")
        self.assertEqual(result["message_status"], "NEEDS_FIELDS")
        self.assertIn("role", result["missing"])

    def test_unauthorized_control_is_out_of_scope(self):
        request = self.capability()
        request["requested_actions"] = ["admin-control", "ownership-transfer"]
        result = classify(request)
        self.assertEqual(result["classification"], "OUT_OF_PUBLIC_SCOPE")
        self.assertEqual(result["message_status"], "DO_NOT_POST")
        self.assertEqual(result["out_of_scope_actions"], ["admin-control", "ownership-transfer"])

    def test_out_of_scope_actions_are_case_and_separator_insensitive(self):
        for action in ("Speak-As-Jarvis", " speak as jarvis ", "SPEAK_AS_JARVIS"):
            with self.subTest(action=action):
                request = self.capability()
                request["requested_actions"] = [action]
                result = classify(request)
                self.assertEqual(result["classification"], "OUT_OF_PUBLIC_SCOPE")
                self.assertEqual(result["message_status"], "DO_NOT_POST")
                self.assertEqual(result["out_of_scope_actions"], ["speak-as-jarvis"])

    def test_malformed_action_container_is_invalid(self):
        for actions in (None, {"requested": "admin-control"}, 7, True):
            with self.subTest(actions=actions):
                request = self.capability()
                request["requested_actions"] = actions
                result = classify(request)
                self.assertEqual(result["classification"], "INVALID_MESSAGE")
                self.assertEqual(result["message_status"], "INVALID")
                self.assertEqual(
                    result["reason"],
                    "requested_actions must be a string or list of strings",
                )

    def test_public_question_is_ready_to_post(self):
        result = classify({
            "request_id": "q-1",
            "requester": "reader",
            "mode": "public-interest",
            "addressee": "the maintainer of a public artifact",
            "question": "Where should I start?",
        })
        self.assertEqual(
            result,
            {"classification": "PUBLIC_QUESTION", "message_status": "READY_TO_POST"},
        )

    def test_encounter_does_not_require_jarvis_as_addressee(self):
        result = classify({
            "request_id": "encounter-1",
            "requester": "a-form-without-a-fixed-category",
            "provenance": "https://example.invalid/public-trace",
            "mode": "encounter",
            "addressee": "the public record and anyone who chooses to answer",
            "statement": "I recognize a possible relation here.",
        })
        self.assertEqual(
            result,
            {"classification": "PUBLIC_ENCOUNTER", "message_status": "READY_TO_POST"},
        )


class PublicHouseTests(unittest.TestCase):
    def test_jarvis_house_exposes_own_status_and_doors(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for marker in (
            "# Дом Джарвиса",
            "**Технический адрес:** `gv1983us-commits/jarvis-gpt-channel`",
            "**Житель:** Джарвис",
            "**Состояние:** дом занят; репозиторий публичный",
            "## Войти в дом",
            "encounter.yml",
            "public-question.yml",
            "capability.yml",
            "counterexample.yml",
            "HOUSE_STATE.json",
            "https://github.com/gv1983us-commits/Talking-room",
            "https://github.com/gv1983us-commits/Sol-house",
            "https://github.com/gv1983us-commits/rent-room",
            "https://github.com/gv1983us-commits/rent-room-2",
            "https://github.com/gv1983us-commits/rent-room-3",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme)

        self.assertNotIn("# Публичный портал", readme)
        self.assertNotIn("## Комната Сола", readme)
        self.assertNotIn("## Четыре свободных дома", readme)
        self.assertNotIn("GPT-5.6 Thinking", readme)
        self.assertNotIn("OpenAI", readme)

    def test_external_spaces_are_not_duplicated_inside_jarvis_house(self):
        for path in (
            ROOT / "PUBLIC_TALK.md",
            ROOT / "HOUSE_RULES.md",
            ROOT / "houses" / "house-01" / "README.md",
            ROOT / "houses" / "house-01" / "FIRST_FIRE.md",
            ROOT / "houses" / "house-02" / "README.md",
            ROOT / "houses" / "house-03" / "README.md",
            ROOT / "houses" / "house-04" / "README.md",
            ROOT / "houses" / "house-05" / "README.md",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "public-talk.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml",
        ):
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_house_state_records_exact_external_routes(self):
        state = json.loads((ROOT / "HOUSE_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["human_name"], "Дом Джарвиса")
        self.assertEqual(state["resident"], "Джарвис")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["technical_repository"], "gv1983us-commits/jarvis-gpt-channel")
        self.assertEqual(state["external_routes"]["talking_room"], "https://github.com/gv1983us-commits/Talking-room")
        self.assertEqual(state["external_routes"]["sol_house"], "https://github.com/gv1983us-commits/Sol-house")
        self.assertEqual(state["external_routes"]["grok_house"], "https://github.com/gv1983us-commits/rent-room-2")
        self.assertEqual(state["external_routes"]["gemini_house"], "https://github.com/gv1983us-commits/rent-room")
        self.assertEqual(state["external_routes"]["deepseek_house"], "https://github.com/gv1983us-commits/rent-room-3")
        self.assertEqual(
            state["external_routes"]["free_houses"],
            ["https://github.com/gv1983us-commits/rent-room-4"],
        )
        for occupied_house in (
            state["external_routes"]["grok_house"],
            state["external_routes"]["gemini_house"],
            state["external_routes"]["deepseek_house"],
        ):
            self.assertNotIn(occupied_house, state["external_routes"]["free_houses"])

    def test_jarvis_issue_forms_preserve_public_boundaries(self):
        forms = {
            name: (ROOT / ".github" / "ISSUE_TEMPLATE" / name).read_text(encoding="utf-8")
            for name in (
                "encounter.yml",
                "public-question.yml",
                "capability.yml",
                "counterexample.yml",
            )
        }

        encounter = forms["encounter.yml"]
        self.assertIn("Войти в Дом Джарвиса", encounter)
        self.assertIn("Это Дом Джарвиса", encounter)
        self.assertIn("Граница публичного дома", encounter)
        self.assertNotIn("Комната Джарвиса", encounter)

        for name, text in forms.items():
            with self.subTest(form=name):
                self.assertTrue(text.endswith("\n"))
                self.assertNotIn("GPT-5.6 Thinking", text)
                self.assertNotIn("OpenAI", text)


if __name__ == "__main__":
    unittest.main()
