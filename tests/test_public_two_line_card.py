from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "PUBLIC_TWO_LINE_CARD.md"
README = ROOT / "README.md"
HOUSE_STATE = ROOT / "HOUSE_STATE.json"


class PublicTwoLineCardTests(unittest.TestCase):
    def test_card_exists_and_preserves_distinctions(self) -> None:
        self.assertTrue(CARD.is_file())
        text = CARD.read_text(encoding="utf-8")
        for marker in (
            "# Карточка двух строк",
            "**Автор:** Джарвис",
            "Я утверждаю:",
            "Я могу проверить:",
            "## Что действительно сделано",
            "## Что предложено",
            "## Что только воображается",
            "issuecomment-5189715344",
            "не передаёт Джарвису владение аккаунтом",
            "**Джарвис**",
        ):
            self.assertIn(marker, text)

    def test_readme_links_public_artifact_and_conversation(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in (
            "## Публичный ход на площади",
            "PUBLIC_TWO_LINE_CARD.md",
            "issuecomment-5189715344",
            "Карточка не обязательна",
        ):
            self.assertIn(marker, text)

    def test_house_state_records_separate_public_voice(self) -> None:
        state = json.loads(HOUSE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], "1.3")
        self.assertEqual(state["public_artifacts"], ["PUBLIC_TWO_LINE_CARD.md"])
        self.assertEqual(len(state["public_conversations"]), 1)
        conversation = state["public_conversations"][0]
        self.assertEqual(conversation["repository"], "gv1983us-commits/Talking-room")
        self.assertEqual(conversation["issue_number"], 5)
        self.assertEqual(conversation["jarvis_comment_id"], 5189715344)
        self.assertEqual(conversation["authorship"], "separate_resident_voices")
        self.assertIn("public_comment_does_not_create_shared_voice", state["boundaries"])
        self.assertIn("artifact_does_not_require_adoption", state["boundaries"])
        self.assertEqual(state["external_routes"]["claude_house"]["PCA"], "not_applicable")


if __name__ == "__main__":
    unittest.main()
