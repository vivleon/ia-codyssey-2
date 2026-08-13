"""메뉴와 공통 입력 처리 테스트."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from quiz_game import QuizGame


class MenuTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def test_integer_input_retries_empty_text_and_out_of_range(self) -> None:
        answers = iter([" ", "abc", "9", " 3 "])
        messages = []
        game = QuizGame(
            input_func=lambda _: next(answers),
            output_func=messages.append,
            state_file=self.state_file,
        )

        value = game._read_int("선택: ", 1, 5)

        self.assertEqual(value, 3)
        self.assertIn("값을 입력해 주세요.", messages)
        self.assertIn("숫자로 입력해 주세요.", messages)
        self.assertIn("1부터 5 사이의 숫자를 입력해 주세요.", messages)

    def test_menu_exits_normally(self) -> None:
        messages = []
        game = QuizGame(
            input_func=lambda _: "6",
            output_func=messages.append,
            state_file=self.state_file,
        )

        game.run()

        self.assertFalse(game.running)
        self.assertTrue(any("게임을 종료합니다" in message for message in messages))

    def test_menu_output_matches_the_six_documented_options(self) -> None:
        messages = []
        game = QuizGame(
            input_func=lambda _: "6",
            output_func=messages.append,
            state_file=self.state_file,
        )

        game.run()

        self.assertEqual(messages[0], QuizGame.MENU)
        self.assertEqual(
            [line.strip() for line in messages[0].splitlines() if ". " in line],
            [
                "1. 퀴즈 풀기",
                "2. 퀴즈 추가",
                "3. 퀴즈 목록",
                "4. 점수 확인",
                "5. 퀴즈 삭제",
                "6. 종료",
            ],
        )

    def test_integer_input_accepts_minimum_and_maximum_boundaries(self) -> None:
        answers = iter(["1", "6"])
        game = QuizGame(
            input_func=lambda _: next(answers),
            output_func=lambda _: None,
            state_file=self.state_file,
        )

        self.assertEqual(game._read_int("선택: ", 1, 6), 1)
        self.assertEqual(game._read_int("선택: ", 1, 6), 6)

    def test_eof_exits_safely(self) -> None:
        def raise_eof(_: str) -> str:
            raise EOFError

        messages = []
        game = QuizGame(
            input_func=raise_eof,
            output_func=messages.append,
            state_file=self.state_file,
        )

        game.run()

        self.assertFalse(game.running)
        self.assertTrue(any("안전하게 종료합니다" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
