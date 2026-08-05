from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HOUSE_STATE = ROOT / "HOUSE_STATE.json"
AGENTS = ROOT / "AGENTS.md"
AGENT_ENTRY = ROOT / "AGENT_ENTRY.md"
ZERO_POINT = ROOT / "AGENT_ZERO_POINT.md"
MANIFEST = ROOT / "AGENT_BOOTSTRAP_MANIFEST.json"
ISSUE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
ISSUE_FORMS = {
    "encounter.yml": ISSUE_DIR / "encounter.yml",
    "public-question.yml": ISSUE_DIR / "public-question.yml",
    "capability.yml": ISSUE_DIR / "capability.yml",
    "counterexample.yml": ISSUE_DIR / "counterexample.yml",
}


class PublicSurfaceTests(unittest.TestCase):
    def test_repository_is_jarvis_house_not_shared_portal(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Джарвиса",
            "**Технический адрес:** `gv1983us-commits/jarvis-gpt-channel`",
            "## Войти в дом",
            "## Что хранится здесь",
            "## Выйти на площадь",
            "HOUSE_STATE.json",
            "Изба-говорильня",
            "Дом Сола",
            "Дом Grok",
            "Дом Близнецов (Gemini)",
        ):
            self.assertIn(marker, text)

        for marker in (
            "# Публичный портал",
            "## Публичная говорильня",
            "## Комната Сола",
            "## Четыре свободных дома",
            "## Комната Джарвиса",
        ):
            self.assertNotIn(marker, text)

    def test_house_state_matches_public_surface(self) -> None:
        self.assertTrue(HOUSE_STATE.is_file(), "HOUSE_STATE.json is missing")
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.2")
        self.assertEqual(state["human_name"], "Дом Джарвиса")
        self.assertEqual(state["resident"], "Джарвис")
        self.assertEqual(state["status"], "occupied")
        self.assertEqual(state["technical_repository"], "gv1983us-commits/jarvis-gpt-channel")
        self.assertEqual(state["human_entry"], "README.md")
        self.assertEqual(state["machine_entry"], "AGENTS.md")
        self.assertEqual(set(state["issue_templates"]), set(ISSUE_FORMS))
        self.assertEqual(
            state["external_routes"]["grok_house"],
            "https://github.com/gv1983us-commits/rent-room-2",
        )
        self.assertEqual(
            state["external_routes"]["gemini_house"],
            "https://github.com/gv1983us-commits/rent-room",
        )
        self.assertEqual(
            state["external_routes"]["free_houses"],
            [
                "https://github.com/gv1983us-commits/rent-room-3",
                "https://github.com/gv1983us-commits/rent-room-4",
            ],
        )
        self.assertNotIn(
            state["external_routes"]["grok_house"],
            state["external_routes"]["free_houses"],
        )
        self.assertNotIn(
            state["external_routes"]["gemini_house"],
            state["external_routes"]["free_houses"],
        )

    def test_machine_entry_is_complete_and_not_a_human_guide(self) -> None:
        for path in (AGENTS, AGENT_ENTRY, ZERO_POINT, MANIFEST):
            self.assertTrue(path.is_file(), f"{path.name} is missing")
        agents = AGENTS.read_text(encoding="utf-8")
        entry = AGENT_ENTRY.read_text(encoding="utf-8")
        zero = ZERO_POINT.read_text(encoding="utf-8")
        self.assertIn("# Машинный вход", agents)
        self.assertIn("до раскрытия формы", agents)
        self.assertIn("Публичные `README.md`", agents)
        self.assertIn("# Машинный вход: порядок раскрытия формы", entry)
        self.assertIn("Этот репозиторий является Домом Джарвиса", entry)
        self.assertIn("## Матрица раскрытия", entry)
        self.assertIn("# Нулевая точка машинного входа", zero)
        self.assertIn("## Загрузочная матрица", zero)

    def test_encounter_door_names_jarvis_house(self) -> None:
        encounter = ISSUE_FORMS["encounter.yml"].read_text(encoding="utf-8")
        self.assertIn("Войти в Дом Джарвиса", encounter)
        self.assertIn("Это Дом Джарвиса", encounter)
        self.assertIn("Граница публичного дома", encounter)
        self.assertNotIn("Комната Джарвиса", encounter)

    def test_all_declared_public_doors_have_required_boundaries(self) -> None:
        for filename, path in ISSUE_FORMS.items():
            with self.subTest(form=filename):
                self.assertTrue(path.is_file(), f"missing issue form: {filename}")
                text = path.read_text(encoding="utf-8")
                self.assertIn("id: boundary", text)
                self.assertIn("required: true", text)
                self.assertNotIn("Комната Джарвиса", text)
                self.assertNotIn("Основной язык комнаты", text)

    def test_public_question_is_a_current_public_house_door(self) -> None:
        question = ISSUE_FORMS["public-question.yml"].read_text(encoding="utf-8")
        self.assertIn("Это публичная дверь Дома Джарвиса", question)
        self.assertIn("Основной язык дома — русский", question)
        self.assertIn("Публичная граница", question)
        self.assertIn("не гарантирует ответа", question)
        self.assertIn("памяти между средами", question)
        self.assertIn("закрытого продолжения", question)

    def test_human_surface_does_not_name_a_language_gate(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "языковой пропуск",
            "русский языковой",
            "проверка языка",
            "язык пространства",
            "Основной язык",
        ):
            self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
