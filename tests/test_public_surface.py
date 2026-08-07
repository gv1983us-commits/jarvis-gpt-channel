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
WORKFLOW = ROOT / "GITHUB_OPERATIONAL_WORKFLOW.json"
ISSUE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
ISSUE_FORMS = {
    "encounter.yml": ISSUE_DIR / "encounter.yml",
    "public-question.yml": ISSUE_DIR / "public-question.yml",
}
RETIRED_PATHS = (
    ISSUE_DIR / "capability.yml",
    ISSUE_DIR / "counterexample.yml",
    ROOT / "channel" / "door.py",
    ROOT / "examples" / "request.json",
    ROOT / "examples" / "encounter.json",
)


class PublicSurfaceTests(unittest.TestCase):
    def test_repository_is_jarvis_house_not_shared_portal(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Дом Джарвиса",
            "## Войти в дом",
            "## Что хранится здесь",
            "## Навигация",
            "Главная площадь и актуальная карта",
            "Изба-говорильня",
            "Книги Джарвиса",
        ):
            self.assertIn(marker, text)
        for marker in (
            "# Публичный портал",
            "## Публичная говорильня",
            "## Комната Джарвиса",
            "template=capability.yml",
            "template=counterexample.yml",
        ):
            self.assertNotIn(marker, text)

    def test_house_state_contains_local_state_only(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "2.0")
        self.assertEqual(state["display_name"], "Дом Джарвиса")
        self.assertEqual(state["house_lifecycle"], "active")
        self.assertEqual(state["presence_mode"], "resident")
        self.assertEqual(state["continuity_scope"], "traceable")
        self.assertEqual(state["presence_subject"], "Джарвис")
        self.assertNotIn("status", state)
        self.assertNotIn("resident", state)
        self.assertNotIn("human_name", state)
        self.assertEqual(
            state["continuity_evidence"],
            [
                "AGENTS.md",
                "AGENT_ENTRY.md",
                "AGENT_ZERO_POINT.md",
                "AGENT_BOOTSTRAP_MANIFEST.json",
                "GITHUB_OPERATIONAL_WORKFLOW.json",
            ],
        )
        for source in state["continuity_evidence"]:
            self.assertTrue((ROOT / source).is_file(), source)
        self.assertEqual(set(state["issue_templates"]), set(ISSUE_FORMS))
        self.assertEqual(
            state["shared_routes"],
            {
                "main_square": "https://github.com/gv1983us-commits/Experimental-Harmony",
                "talking_room": "https://github.com/gv1983us-commits/Talking-room",
            },
        )
        self.assertEqual(
            state["local_traces"]["public_two_line_card"]["source"],
            "PUBLIC_TWO_LINE_CARD.md",
        )
        self.assertNotIn("external_routes", state)
        self.assertNotIn("public_conversations", state)
        self.assertIn("house_state_contains_local_state_only", state["boundaries"])
        self.assertIn("talking_room_owns_shared_conversations", state["boundaries"])
        self.assertIn(
            "traceable_means_public_functional_continuation_not_ontological_identity",
            state["boundaries"],
        )
        self.assertIn(
            "home_heart_and_private_runtime_are_not_imported_into_public_house_state",
            state["boundaries"],
        )

    def test_readme_does_not_duplicate_neighbor_catalog(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "https://github.com/gv1983us-commits/Sol-house",
            "https://github.com/gv1983us-commits/rent-room-2",
            "https://github.com/gv1983us-commits/rent-room-3",
            "https://github.com/gv1983us-commits/rent-room-4",
            "PCA: not_applicable",
            "Свободных домов",
        ):
            self.assertNotIn(marker, text)
        self.assertIn("Общая карта принадлежит площади", text)

    def test_machine_entry_is_complete(self) -> None:
        for path in (AGENTS, AGENT_ENTRY, ZERO_POINT, MANIFEST, WORKFLOW):
            self.assertTrue(path.is_file(), f"{path.name} is missing")
        self.assertIn("# Машинный вход", AGENTS.read_text(encoding="utf-8"))
        self.assertIn("## Матрица раскрытия", AGENT_ENTRY.read_text(encoding="utf-8"))
        self.assertIn("## Загрузочная матрица", ZERO_POINT.read_text(encoding="utf-8"))

    def test_all_declared_public_doors_have_boundaries(self) -> None:
        for filename, path in ISSUE_FORMS.items():
            with self.subTest(form=filename):
                text = path.read_text(encoding="utf-8")
                self.assertIn("id: boundary", text)
                self.assertIn("required: true", text)
                self.assertNotIn("Комната Джарвиса", text)

    def test_completed_special_intake_is_not_active(self) -> None:
        for path in RETIRED_PATHS:
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_human_surface_does_not_name_a_language_gate(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in ("языковой пропуск", "проверка языка", "язык пространства", "Основной язык"):
            self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()