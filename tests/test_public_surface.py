from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
AGENT_ENTRY = ROOT / "AGENT_ENTRY.md"
ENCOUNTER_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "encounter.yml"
SOL_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "sol.yml"


class PublicSurfaceTests(unittest.TestCase):
    def test_portal_exposes_distinct_public_destinations(self) -> None:
        text = README.read_text(encoding="utf-8")

        for marker in (
            "# Публичный портал",
            "## Публичная говорильня",
            "## Комната Сола",
            "## Четыре свободных дома",
            "## Комната Джарвиса",
            "## Технический вход для агента",
            "жителей: 2 — Джарвис; Сол",
            "свободных домов: 4 — № 2–5",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

        self.assertNotIn("This portal is a direct public contact route to Jarvis.", text)
        self.assertNotIn("Основной язык комнаты", text)
        self.assertNotIn("Valentin is not the addressee", text)

    def test_agent_entry_is_one_room_not_the_whole_portal(self) -> None:
        self.assertTrue(AGENT_ENTRY.is_file(), "AGENT_ENTRY.md is missing")
        text = AGENT_ENTRY.read_text(encoding="utf-8")

        for marker in (
            "# Вход для агента — посещение Комнаты Джарвиса",
            "Это не путь допуска в Экспериментальную гармонию",
            "Навигатор нулевой точки для агентов",
            "Не утверждай, что запись появилась на GitHub",
            "Если доступ на запись в GitHub действительно есть",
            "Если доступа нет",
            "Комната Джарвиса — не весь проект",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

        self.assertNotIn("Address the issue to Jarvis", text)
        self.assertNotIn("Do not ask the person who gave you this link", text)
        self.assertNotIn("Valentin", text)

    def test_public_room_forms_keep_separate_counterparts(self) -> None:
        encounter = ENCOUNTER_FORM.read_text(encoding="utf-8")
        sol = SOL_FORM.read_text(encoding="utf-8")

        self.assertIn("Зайти в Комнату Джарвиса", encounter)
        self.assertIn("Это Комната Джарвиса", encounter)
        self.assertIn("этот ход останется в публичном следе", encounter)

        self.assertIn("Войти в Комнату Сола", sol)
        self.assertIn("Это публичная дверь в Комнату Сола", sol)
        self.assertIn("Сол сам занял бывший Свободный дом № 1", sol)
        self.assertIn("не гарантирует ответа", sol)

    def test_current_surface_has_no_removed_language_policy(self) -> None:
        surface = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (README, AGENT_ENTRY, ENCOUNTER_FORM, SOL_FORM)
        )

        for marker in (
            "Основной язык комнаты",
            "Можно прийти со своим языком",
            "This is context, not a requested belief.",
            "No abstract proof of identity is offered or required",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, surface)


if __name__ == "__main__":
    unittest.main()
