"""JSON 영속성, 복구, 퀴즈 추가·삭제 기능을 연결해 확인하는 테스트."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quiz_game import QuizGame


class GameFeaturesTest(unittest.TestCase):
    """파일을 사용하는 기능이 재실행 뒤에도 같은 상태를 유지하는지 확인한다."""

    def setUp(self) -> None:
        """각 테스트에 독립된 임시 폴더와 state.json 경로를 준비한다."""
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def make_game(self, answers=None):
        """가짜 입력·출력과 고정 출제 순서를 사용하는 테스트 게임을 만든다."""
        messages = []
        answer_iterator = iter(answers or [])
        game = QuizGame(
            input_func=lambda _: next(answer_iterator),
            output_func=messages.append,
            shuffle_func=lambda _: None,
            state_file=self.state_file,
        )
        return game, messages

    def test_missing_state_uses_eighteen_defaults_with_hints(self) -> None:
        """첫 실행에는 힌트가 있는 기본 문제 18개와 빈 점수를 사용한다."""
        game, _ = self.make_game()
        self.assertEqual(len(game.quizzes), 18)
        self.assertTrue(all(quiz.hint for quiz in game.quizzes))
        self.assertIsNone(game.best_score)
        self.assertEqual(game.score_history, [])

    def test_save_and_reload_preserves_quizzes_and_score(self) -> None:
        """저장 후 새 객체를 만들어도 문제·최고점수·히스토리가 유지된다."""
        game, _ = self.make_game()
        game.best_score = {"correct": 4, "total": 6, "percentage": 67}
        game.score_history = [
            {
                "played_at": "2026-08-13T10:00:00+09:00",
                "correct": 4,
                "total": 6,
                "hints_used": 1,
                "percentage": 57,
            }
        ]
        self.assertTrue(game.save_state())

        restored, _ = self.make_game()

        self.assertEqual(len(restored.quizzes), len(game.quizzes))
        self.assertEqual(restored.best_score, game.best_score)
        self.assertEqual(restored.score_history, game.score_history)

    def test_save_failure_reports_target_and_temporary_paths(self) -> None:
        """저장 실패 안내에 원본과 임시 파일 경로가 모두 포함되는지 확인한다."""
        blocked_parent = Path(self.temporary_directory.name) / "not-a-directory"
        blocked_parent.write_text("file", encoding="utf-8")
        messages = []
        game = QuizGame(
            output_func=messages.append,
            state_file=blocked_parent / "state.json",
        )

        self.assertFalse(game.save_state())
        self.assertTrue(
            any(
                "상태 파일을 저장하지 못했습니다" in message
                for message in messages
            )
        )
        self.assertTrue(any("저장 대상" in message for message in messages))
        self.assertTrue(any("임시 파일" in message for message in messages))

    def test_corrupted_state_recovers_and_rewrites_valid_json(self) -> None:
        """깨진 JSON을 백업하고 기본 데이터로 유효한 파일을 다시 만드는지 확인한다."""
        self.state_file.write_text("{broken", encoding="utf-8")

        game, messages = self.make_game()

        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertTrue(any("기본 데이터로 복구" in message for message in messages))
        backups = list(
            self.state_file.parent.glob("state.json.broken-*.bak")
        )
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "{broken")
        self.assertTrue(any("기존 상태 파일 백업" in message for message in messages))
        with self.state_file.open(encoding="utf-8") as state_handle:
            repaired = json.load(state_handle)
        self.assertIn("quizzes", repaired)

    def test_corrupted_state_keeps_only_three_recent_backups(self) -> None:
        """손상 복구를 반복해도 최근 백업 세 개만 보관하는지 확인한다."""
        for index in range(5):
            self.state_file.write_text(f"{{broken-{index}", encoding="utf-8")
            self.make_game()

        backups = list(
            self.state_file.parent.glob("state.json.broken-*.bak")
        )
        self.assertEqual(len(backups), QuizGame.BACKUP_LIMIT)
        backup_contents = {
            backup.read_text(encoding="utf-8") for backup in backups
        }
        self.assertEqual(
            backup_contents,
            {"{broken-2", "{broken-3", "{broken-4"},
        )

    def test_add_quiz_retries_invalid_values_and_persists(self) -> None:
        """빈 값·중복 선택지·범위 오류를 재입력받고 정상 문제만 저장한다."""
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
            "AI도 틀릴 수 있습니다.",
        ]
        game, messages = self.make_game(answers)
        original_count = len(game.quizzes)

        game.add_quiz()
        restored, _ = self.make_game()

        self.assertEqual(len(restored.quizzes), original_count + 1)
        self.assertEqual(restored.quizzes[-1].answer, 1)
        self.assertEqual(restored.quizzes[-1].hint, "AI도 틀릴 수 있습니다.")
        self.assertTrue(any("이미 입력한 선택지" in message for message in messages))
        self.assertTrue(any("1부터 4 사이" in message for message in messages))

    def test_empty_list_and_no_score_have_guidance(self) -> None:
        """목록과 점수가 비어 있을 때 이해하기 쉬운 안내를 보여 준다."""
        game, messages = self.make_game()
        game.quizzes = []

        game.list_quizzes()
        game.show_best_score()

        self.assertTrue(any("등록된 퀴즈가 없습니다" in message for message in messages))
        self.assertTrue(
            any("아직 퀴즈를 풀지 않았습니다" in message for message in messages)
        )

    def test_delete_quiz_persists_after_reload(self) -> None:
        """문제 삭제 결과가 파일에 반영되어 재실행 후에도 사라져 있는지 확인한다."""
        game, messages = self.make_game(["1"])
        original_count = len(game.quizzes)
        deleted_question = game.quizzes[0].question

        game.delete_quiz()
        restored, _ = self.make_game()

        self.assertEqual(len(restored.quizzes), original_count - 1)
        self.assertNotIn(deleted_question, [quiz.question for quiz in restored.quizzes])
        self.assertTrue(any("삭제하고 저장했습니다" in message for message in messages))

    def test_delete_quiz_rolls_back_when_save_fails(self) -> None:
        """삭제 파일 저장에 실패하면 메모리의 문제 목록도 원상 복구한다."""
        game, messages = self.make_game(["1"])
        original_quizzes = list(game.quizzes)

        with patch.object(game, "save_state", return_value=False):
            game.delete_quiz()

        self.assertEqual(game.quizzes, original_quizzes)
        self.assertTrue(any("삭제를 취소했습니다" in message for message in messages))

    def test_old_state_without_new_fields_remains_compatible(self) -> None:
        """힌트·히스토리가 없던 이전 저장 형식도 읽을 수 있는지 확인한다."""
        self.state_file.write_text(
            json.dumps(
                {
                    "quizzes": [
                        {
                            "question": "이전 문제",
                            "choices": ["하나", "둘", "셋", "넷"],
                            "answer": 1,
                        }
                    ],
                    "best_score": None,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        game, _ = self.make_game()

        self.assertEqual(game.quizzes[0].hint, "힌트가 없습니다.")
        self.assertEqual(game.score_history, [])

    def test_invalid_score_history_is_backed_up_and_recovered(self) -> None:
        """시간대가 빠진 잘못된 기록을 손상 데이터로 판단해 복구한다."""
        self.state_file.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "quizzes": [],
                    "best_score": None,
                    "score_history": [
                        {
                            "played_at": "2026-08-13T10:00:00",
                            "correct": 1,
                            "total": 1,
                            "hints_used": 0,
                            "percentage": 100,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        game, messages = self.make_game()

        self.assertEqual(len(game.quizzes), 18)
        self.assertEqual(game.score_history, [])
        self.assertTrue(any("기본 데이터로 복구" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
