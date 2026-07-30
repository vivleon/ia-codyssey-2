"""영속성, 퀴즈 추가, 조회 기능 통합 테스트."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from quiz_game import QuizGame


class GameFeaturesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def make_game(self, answers=None):
        messages = []
        answer_iterator = iter(answers or [])
        game = QuizGame(
            input_func=lambda _: next(answer_iterator),
            output_func=messages.append,
            shuffle_func=lambda _: None,
            state_file=self.state_file,
        )
        return game, messages

    def test_missing_state_uses_at_least_five_defaults(self) -> None:
        game, _ = self.make_game()
        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertIsNone(game.best_score)

    def test_save_and_reload_preserves_quizzes_and_score(self) -> None:
        game, _ = self.make_game()
        game.best_score = {"correct": 4, "total": 6, "percentage": 67}
        self.assertTrue(game.save_state())

        restored, _ = self.make_game()

        self.assertEqual(len(restored.quizzes), len(game.quizzes))
        self.assertEqual(restored.best_score, game.best_score)

    def test_corrupted_state_recovers_and_rewrites_valid_json(self) -> None:
        self.state_file.write_text("{broken", encoding="utf-8")

        game, messages = self.make_game()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertTrue(any("기본 데이터로 복구" in message for message in messages))
        with self.state_file.open(encoding="utf-8") as state_handle:
            repaired = json.load(state_handle)
        self.assertIn("quizzes", repaired)

    def test_add_quiz_retries_invalid_values_and_persists(self) -> None:
        answers = [
            "",
            "AI의 답을 검증해야 하는 이유는?",
            "오류가 있을 수 있어서",
            "오류가 있을 수 있어서",
            "화면이 커져서",
            "전기가 절약돼서",
            "키보드가 바뀌어서",
            "0",
            "1",
        ]
        game, messages = self.make_game(answers)
        original_count = len(game.quizzes)

        game.add_quiz()
        restored, _ = self.make_game()

        self.assertEqual(len(restored.quizzes), original_count + 1)
        self.assertEqual(restored.quizzes[-1].answer, 1)
        self.assertTrue(any("이미 입력한 선택지" in message for message in messages))
        self.assertTrue(any("1부터 4 사이" in message for message in messages))

    def test_empty_list_and_no_score_have_guidance(self) -> None:
        game, messages = self.make_game()
        game.quizzes = []

        game.list_quizzes()
        game.show_best_score()

        self.assertTrue(any("등록된 퀴즈가 없습니다" in message for message in messages))
        self.assertTrue(any("아직 퀴즈를 풀지 않았습니다" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
