"""JSON 저장과 불러오기 테스트"""

import json
import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from storage import load_state, save_state


class StorageTest(unittest.TestCase):
    def setUp(self):
        # 실제 state.json 대신 임시 폴더를 사용한다.
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.filename = os.path.join(self.folder.name, "state.json")

    def test_missing_file_uses_defaults(self):
        quizzes, best_score, history = load_state(self.filename)

        self.assertEqual(len(quizzes), 18)
        self.assertIsNone(best_score)
        self.assertEqual(history, [])

    def test_save_and_load(self):
        quizzes, best_score, history = load_state(self.filename)
        best_score = {
            "correct": 1,
            "total": 1,
            "percentage": 100,
            "hints_used": 0,
        }

        self.assertTrue(save_state(self.filename, quizzes, best_score, history))

        with patch("builtins.print"):
            new_quizzes, new_best, new_history = load_state(self.filename)

        self.assertEqual(len(new_quizzes), 18)
        self.assertEqual(new_best, best_score)
        self.assertEqual(new_history, [])

    def test_broken_file_is_recovered_and_backed_up(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write("{broken")

        with patch("builtins.print"):
            quizzes, best_score, history = load_state(self.filename)

        self.assertEqual(len(quizzes), 18)
        self.assertIsNone(best_score)
        self.assertEqual(history, [])
        self.assertTrue(os.path.exists(self.filename + ".bak"))

        # 복구된 state.json은 다시 읽을 수 있는 JSON이어야 한다.
        with open(self.filename, "r", encoding="utf-8") as file:
            repaired = json.load(file)

        self.assertIn("quizzes", repaired)

    def test_wrong_history_is_recovered(self):
        # 시간대가 없는 게임 기록은 잘못된 상태로 처리한다.
        quizzes, best_score, history = load_state(self.filename)
        history.append(
            {
                "played_at": "2026-08-14T10:00:00",
                "correct": 1,
                "total": 1,
                "percentage": 100,
                "hints_used": 0,
            }
        )
        save_state(self.filename, quizzes, best_score, history)

        with patch("builtins.print"):
            new_quizzes, new_best, new_history = load_state(self.filename)

        self.assertEqual(len(new_quizzes), 18)
        self.assertIsNone(new_best)
        self.assertEqual(new_history, [])


if __name__ == "__main__":
    unittest.main()
