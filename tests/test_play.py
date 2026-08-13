"""퀴즈 출제와 점수 계산 테스트."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quiz_game import QuizGame


class PlayQuizTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def make_game(self, answers):
        messages = []
        answer_iterator = iter(answers)
        game = QuizGame(
            input_func=lambda _: next(answer_iterator),
            output_func=messages.append,
            shuffle_func=lambda _: None,
            state_file=self.state_file,
        )
        game.quizzes = game.quizzes[:2]
        return game, messages

    def test_all_correct_answers_set_best_score(self) -> None:
        game, messages = self.make_game(["2", "2", "1"])

        game.play_quiz()

        self.assertEqual(
            game.best_score,
            {"correct": 2, "total": 2, "percentage": 100, "hints_used": 0},
        )
        self.assertTrue(any("새로운 최고 점수" in message for message in messages))
        self.assertEqual(len(game.score_history), 1)

    def test_new_best_score_is_saved_immediately(self) -> None:
        game, messages = self.make_game(["2", "2", "1"])

        game.play_quiz()
        restored = QuizGame(
            output_func=lambda _: None,
            state_file=self.state_file,
        )

        self.assertEqual(restored.best_score, game.best_score)
        self.assertEqual(restored.score_history, game.score_history)
        self.assertTrue(
            any("상태 파일에 저장되었습니다" in message for message in messages)
        )

    def test_new_best_score_reports_immediate_save_failure(self) -> None:
        game, messages = self.make_game(["2", "2", "1"])

        with patch.object(game, "save_state", return_value=False):
            game.play_quiz()

        self.assertEqual(game.best_score["percentage"], 100)
        self.assertTrue(
            any("최고 점수는 갱신되었지만" in message for message in messages)
        )

    def test_lower_score_does_not_replace_best(self) -> None:
        game, _ = self.make_game(["2", "1", "1"])
        game.best_score = {"correct": 2, "total": 2, "percentage": 100}

        game.play_quiz()

        self.assertEqual(game.best_score["percentage"], 100)
        self.assertEqual(len(game.score_history), 1)

    def test_player_selects_question_count(self) -> None:
        game, messages = self.make_game(["1", "2"])

        game.play_quiz()

        self.assertEqual(game.score_history[0]["total"], 1)
        self.assertTrue(any("총 1문제" in message for message in messages))

    def test_questions_are_shuffled_before_selection(self) -> None:
        shuffled = []
        answers = iter(["1", "1"])

        def reverse_questions(questions) -> None:
            questions.reverse()
            shuffled.append(True)

        game = QuizGame(
            input_func=lambda _: next(answers),
            output_func=lambda _: None,
            shuffle_func=reverse_questions,
            state_file=self.state_file,
        )
        game.quizzes = game.quizzes[:2]

        game.play_quiz()

        self.assertEqual(shuffled, [True])
        self.assertEqual(game.score_history[0]["correct"], 1)

    def test_hint_is_shown_once_and_deducts_ten_points(self) -> None:
        game, messages = self.make_game(["1", "h", "h", "2"])

        game.play_quiz()

        self.assertEqual(game.best_score["correct"], 1)
        self.assertEqual(game.best_score["hints_used"], 1)
        self.assertEqual(game.best_score["percentage"], 90)
        self.assertTrue(any("💡 힌트:" in message for message in messages))
        self.assertTrue(any("이미 사용했습니다" in message for message in messages))

    def test_every_completed_game_is_saved_to_history(self) -> None:
        game, _ = self.make_game(["1", "2"])
        game.play_quiz()
        second_answers = iter(["1", "1"])
        game.input = lambda _: next(second_answers)

        game.play_quiz()
        restored = QuizGame(output_func=lambda _: None, state_file=self.state_file)

        self.assertEqual(len(restored.score_history), 2)
        self.assertEqual(restored.score_history[0]["percentage"], 100)
        self.assertEqual(restored.score_history[1]["percentage"], 0)

    def test_empty_quiz_list_is_handled(self) -> None:
        game, messages = self.make_game([])
        game.quizzes = []

        game.play_quiz()

        self.assertTrue(any("등록된 퀴즈가 없습니다" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
