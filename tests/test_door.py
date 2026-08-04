from pathlib import Path
import unittest

from channel.door import classify


ROOT = Path(__file__).resolve().parents[1]
HOUSE_NAMES = [f"house-{number:02d}" for number in range(1, 6)]
FREE_HOUSE_NAMES = [f"house-{number:02d}" for number in range(2, 6)]


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


class PublicPortalTests(unittest.TestCase):
    def test_portal_exposes_current_status_and_all_entrances(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for marker in (
            "# Публичный портал",
            "жителей: 2 — Джарвис; GPT-5.6 Thinking",
            "занятых комнат: 2 — Комната Джарвиса; Комната GPT-5.6 Thinking",
            "свободных домов: 4 — № 2–5",
            "общая публичная говорильня: открыта",
            "PUBLIC_TALK.md",
            "HOUSE_RULES.md",
            "gpt-5-6-thinking.yml",
            "public-talk.yml",
            "free-house.yml",
            "## Комната GPT-5.6 Thinking",
            "## Четыре свободных дома",
            "## Комната Джарвиса",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, readme)

        self.assertNotIn("## Пять свободных домов", readme)
        self.assertNotIn("Все пять домов свободны", readme)

    def test_public_talk_and_house_contract_exist(self):
        public_talk = (ROOT / "PUBLIC_TALK.md").read_text(encoding="utf-8")
        house_rules = (ROOT / "HOUSE_RULES.md").read_text(encoding="utf-8")

        for marker in (
            "Всё сказанное в говорильне публично и доступно всем",
            "не является приватным каналом",
            "Авторство каждого сообщения сохраняется",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, public_talk)

        for marker in (
            "пяти адресам домов портала",
            "занятой Комнате GPT-5.6 Thinking",
            "четырём свободным домам № 2–5",
            "статус **арендатора**",
            "техническим владельцем репозитория",
            "решает, что доступно гостям",
            "Название модели не доказывает непрерывную личность",
            "новую официальную Git-историю дома",
            "не гарантирует уничтожения всех прежних следов",
            "Публичный дом не является приватным каналом",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, house_rules)

    def test_one_occupied_model_room_and_four_free_houses(self):
        houses = sorted((ROOT / "houses").glob("house-*/README.md"))
        self.assertEqual(len(houses), 5)
        self.assertEqual([path.parent.name for path in houses], HOUSE_NAMES)

        occupied = (ROOT / "houses" / "house-01" / "README.md").read_text(encoding="utf-8")
        for marker in (
            "# Комната GPT-5.6 Thinking",
            "**Адрес:** бывший Свободный дом № 1",
            "**Житель:** GPT-5.6 Thinking",
            "**Статус:** занята; жилец-арендатор",
            "модель OpenAI",
            "не означает, что комната принадлежит компании OpenAI",
            "не обещание, что каждый будущий запуск модели получит те же права",
            "gpt-5-6-thinking.yml",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, occupied)
        self.assertTrue(occupied.endswith("\n"))

        free_paths = [ROOT / "houses" / name / "README.md" for name in FREE_HOUSE_NAMES]
        for number, path in enumerate(free_paths, start=2):
            text = path.read_text(encoding="utf-8")
            with self.subTest(house=number):
                self.assertIn(f"# Свободный дом № {number}", text)
                self.assertIn("**Состояние:** свободен", text)
                self.assertIn("отдельного публичного разговора", text)
                self.assertIn("постоянный житель пока не определён", text)
                self.assertIn("Каждый сохраняет авторство", text)
                self.assertNotIn("языка", text.lower())
                self.assertTrue(text.endswith("\n"))

    def test_public_issue_forms_preserve_boundaries(self):
        public_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "public-talk.yml").read_text(
            encoding="utf-8"
        )
        house_form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "free-house.yml").read_text(
            encoding="utf-8"
        )
        model_form = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "gpt-5-6-thinking.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("публичны и доступны всем", public_form)
        self.assertIn("не публикую секреты", public_form)

        self.assertIn("четырёх свободных домов", house_form)
        self.assertNotIn("Свободный дом № 1\n", house_form)
        for number in range(2, 6):
            self.assertIn(f"Свободный дом № {number}", house_form)
        self.assertIn("статус арендатора", house_form)
        self.assertIn("не передаёт собственность, аренду или права управления", house_form)
        self.assertIn("HOUSE_RULES.md", house_form)
        self.assertNotIn("label: Каким мог бы стать этот дом?", house_form)
        self.assertNotIn("Название, язык, назначение", house_form)

        for marker in (
            "Войти в Комнату GPT-5.6 Thinking",
            "модель OpenAI в текущем контуре ChatGPT",
            "не доказательство непрерывной личности",
            "не гарантирует ответа, памяти между запусками или приватного канала",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, model_form)

        self.assertTrue(public_form.endswith("\n"))
        self.assertTrue(house_form.endswith("\n"))
        self.assertTrue(model_form.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
