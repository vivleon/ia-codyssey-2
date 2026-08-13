"""문제 선택, 랜덤 출제, 힌트 감점, 점수 저장의 통합 테스트."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quiz_game import QuizGame


class PlayQuizTest(unittest.TestCase):
    """퀴즈 한 게임이 시작부터 기록 저장까지 올바르게 연결되는지 확인한다."""

    def setUp(self) -> None:
        """실제 사용자 파일을 건드리지 않는 임시 state.json 경로를 만든다."""
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def make_game(self, answers):
        """정해 둔 답을 순서대로 입력하고 출력은 목록에 모으는 게임을 만든다."""
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
        """모든 문제를 맞히면 100점 최고 기록과 히스토리가 생기는지 확인한다."""
        game, messages = self.make_game(["2", "2", "1"])

        game.play_quiz()

        self.assertEqual(
            game.best_score,
            {"correct": 2, "total": 2, "percentage": 100, "hints_used": 0},
        )
        self.assertTrue(any("새로운 최고 점수" in message for message in messages))
        self.assertEqual(len(game.score_history), 1)

    def test_new_best_score_is_saved_immediately(self) -> None:
        """새 최고 점수가 게임 직후 저장되어 재실행해도 유지되는지 확인한다."""
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
        """최고점수 갱신 후 파일 저장 실패를 사용자에게 알리는지 확인한다."""
        game, messages = self.make_game(["2", "2", "1"])

        with patch.object(game, "save_state", return_value=False):
            game.play_quiz()

        self.assertEqual(game.best_score["percentage"], 100)
        self.assertTrue(
            any("최고 점수는 갱신되었지만" in message for message in messages)
        )

    def test_lower_score_does_not_replace_best(self) -> None:
        """낮은 점수는 기존 최고 점수를 덮지 않고 히스토리에만 남는지 확인한다."""
        game, _ = self.make_game(["2", "1", "1"])
        game.best_score = {"correct": 2, "total": 2, "percentage": 100}

        game.play_quiz()

        self.assertEqual(game.best_score["percentage"], 100)
        self.assertEqual(len(game.score_history), 1)

    def test_player_selects_question_count(self) -> None:
        """사용자가 선택한 문제 수만 출제하고 결과에도 같은 수를 기록한다."""
        game, messages = self.make_game(["1", "2"])

        game.play_quiz()

        self.assertEqual(game.score_history[0]["total"], 1)
        self.assertTrue(any("총 1문제" in message for message in messages))

    def test_questions_are_shuffled_before_selection(self) -> None:
        """문제 수를 자르기 전에 shuffle 함수가 호출되는지 확인한다."""
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
        """한 문제의 힌트는 한 번만 인정되고 최종 점수에서 10점 차감된다."""
        game, messages = self.make_game(["1", "h", "h", "2"])

        game.play_quiz()

        self.assertEqual(game.best_score["correct"], 1)
        self.assertEqual(game.best_score["hints_used"], 1)
        self.assertEqual(game.best_score["percentage"], 90)
        self.assertTrue(any("💡 힌트:" in message for message in messages))
        self.assertTrue(any("이미 사용했습니다" in message for message in messages))

    def test_every_completed_game_is_saved_to_history(self) -> None:
        """두 번 플레이한 모든 결과가 순서대로 저장·복원되는지 확인한다."""
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
        """문제가 하나도 없을 때 오류 대신 추가 안내를 보여 주는지 확인한다."""
        game, messages = self.make_game([])
        game.quizzes = []

        game.play_quiz()

        self.assertTrue(any("등록된 퀴즈가 없습니다" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
