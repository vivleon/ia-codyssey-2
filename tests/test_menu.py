"""메뉴 반복, 정수 입력 검증, 안전 종료를 확인하는 단위 테스트."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from quiz_game import QuizGame


class MenuTest(unittest.TestCase):
    """사용자가 프로그램에 처음 접하는 메뉴와 입력 경계를 검증한다."""

    def setUp(self) -> None:
        """실제 state.json 대신 테스트마다 독립된 임시 경로를 준비한다."""
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.state_file = Path(self.temporary_directory.name) / "state.json"

    def test_integer_input_retries_empty_text_and_out_of_range(self) -> None:
        """빈 값·문자·범위 밖 숫자 뒤 유효한 입력을 받을 때까지 반복한다."""
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
        """6번을 선택하면 반복 조건이 꺼지고 정상 종료 문구가 나오는지 확인한다."""
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
        """실제 메뉴의 여섯 항목이 README에 설명한 기능과 같은지 확인한다."""
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
        """정수 입력 범위의 최솟값과 최댓값을 모두 허용하는지 확인한다."""
        answers = iter(["1", "6"])
        game = QuizGame(
            input_func=lambda _: next(answers),
            output_func=lambda _: None,
            state_file=self.state_file,
        )

        self.assertEqual(game._read_int("선택: ", 1, 6), 1)
        self.assertEqual(game._read_int("선택: ", 1, 6), 6)

    def test_eof_exits_safely(self) -> None:
        """입력 스트림이 끝나도 예외를 노출하지 않고 안전 종료하는지 확인한다."""
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
