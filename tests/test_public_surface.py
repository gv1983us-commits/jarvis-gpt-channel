from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
AGENT_ENTRY = ROOT / "AGENT_ENTRY.md"
ZERO_POINT = ROOT / "AGENT_ZERO_POINT.md"
MANIFEST = ROOT / "AGENT_BOOTSTRAP_MANIFEST.json"
ENCOUNTER_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "encounter.yml"
SOL_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml"


class PublicSurfaceTests(unittest.TestCase):
    def test_portal_exposes_only_human_destinations(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "# Публичный портал",
            "## Публичная говорильня",
            "## Комната Сола",
            "## Четыре свободных дома",
            "## Комната Джарвиса",
            "жителей: 2 — Джарвис; Сол",
            "свободных домов: 4 — № 2–5",
        ):
            self.assertIn(marker, text)
        for marker in (
            "AGENT_",
            "AGENTS.md",
            "Навигатор нулевой точки",
            "машинный",
            "модель",
            "runtime",
            "bootstrap",
            "спецификац",
            "## Технический вход",
        ):
            self.assertNotIn(marker, text)

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
        self.assertIn("## Матрица раскрытия", entry)
        self.assertIn("# Нулевая точка машинного входа", zero)
        self.assertIn("## Загрузочная матрица", zero)

    def test_public_room_forms_keep_separate_counterparts(self) -> None:
        encounter = ENCOUNTER_FORM.read_text(encoding="utf-8")
        sol = SOL_FORM.read_text(encoding="utf-8")
        self.assertIn("Зайти в Комнату Джарвиса", encounter)
        self.assertIn("Это Комната Джарвиса", encounter)
        self.assertIn("Войти в Комнату Сола", sol)
        self.assertIn("Это публичная дверь в Комнату Сола", sol)

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
