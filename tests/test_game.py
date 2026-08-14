"""메뉴와 보너스 기능 테스트"""

import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quiz_game import QuizGame


class GameTest(unittest.TestCase):
    def setUp(self):
        # 테스트마다 새로운 임시 state.json을 사용한다.
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.filename = os.path.join(self.folder.name, "state.json")

    def make_game(self):
        with patch("builtins.print"):
            return QuizGame(self.filename)

    def test_wrong_number_is_asked_again(self):
        game = self.make_game()

        with patch("builtins.input", side_effect=["", "abc", "9", "2"]):
            with patch("builtins.print"):
                number = game.read_number("선택: ", 1, 6)

        self.assertEqual(number, 2)

    def test_menu_can_exit(self):
        game = self.make_game()

        with patch("builtins.input", return_value="6"):
            with patch("builtins.print"):
                game.run()

        self.assertFalse(game.running)
        self.assertTrue(os.path.exists(self.filename))

    def test_hint_deducts_score_and_history_is_saved(self):
        game = self.make_game()
        game.quizzes = game.quizzes[:1]

        # 1문제를 고르고, 힌트를 본 뒤 정답 2번을 고른다.
        with patch("random.shuffle") as fake_shuffle:
            with patch("builtins.input", side_effect=["1", "h", "2"]):
                with patch("builtins.print"):
                    game.play_quiz()

        fake_shuffle.assert_called_once()
        self.assertEqual(game.best_score["total"], 1)
        self.assertEqual(game.best_score["percentage"], 90)
        self.assertEqual(game.best_score["hints_used"], 1)
        self.assertEqual(len(game.score_history), 1)
        self.assertIn("played_at", game.score_history[0])

    def test_add_and_delete_quiz(self):
        game = self.make_game()
        old_count = len(game.quizzes)

        answers = ["새 문제", "하나", "둘", "셋", "넷", "2", "새 힌트"]

        with patch("builtins.input", side_effect=answers):
            with patch("builtins.print"):
                game.add_quiz()

        self.assertEqual(len(game.quizzes), old_count + 1)

        # 마지막 번호를 선택해 방금 추가한 문제를 삭제한다.
        last_number = str(len(game.quizzes))

        with patch("builtins.input", return_value=last_number):
            with patch("builtins.print"):
                game.delete_quiz()

        self.assertEqual(len(game.quizzes), old_count)

        with patch("builtins.print"):
            restored = QuizGame(self.filename)

        self.assertEqual(len(restored.quizzes), old_count)

    def test_eof_exits_safely(self):
        game = self.make_game()

        with patch("builtins.input", side_effect=EOFError):
            with patch("builtins.print"):
                game.run()

        self.assertTrue(os.path.exists(self.filename))


if __name__ == "__main__":
    unittest.main()
