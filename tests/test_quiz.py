"""Quiz 모델만 독립적으로 확인하는 단위 테스트.

단위 테스트는 작은 함수나 클래스 하나의 규칙을 빠르게 검증한다.
"""

import unittest

from quiz import Quiz


class QuizTest(unittest.TestCase):
    """Quiz의 정답 판정, 변환, 입력 검증 규칙을 확인한다."""

    def setUp(self) -> None:
        """각 테스트가 공통으로 사용할 정상 Quiz를 새로 만든다."""
        self.quiz = Quiz(
            "Python에서 목록을 표현하는 자료형은?",
            ["int", "str", "list", "bool"],
            3,
            "대괄호를 사용하는 자료형입니다.",
        )

    def test_checks_answer(self) -> None:
        """정답 번호에는 True, 다른 번호에는 False가 반환되는지 확인한다."""
        self.assertTrue(self.quiz.is_correct(3))
        self.assertFalse(self.quiz.is_correct(1))

    def test_accepts_first_and_last_answer_boundaries(self) -> None:
        """허용 범위의 경계값인 1번과 4번 정답이 통과하는지 확인한다."""
        choices = ["하나", "둘", "셋", "넷"]
        first_answer = Quiz("첫 번째가 정답인 문제", choices, 1)
        last_answer = Quiz("마지막이 정답인 문제", choices, 4)

        self.assertTrue(first_answer.is_correct(1))
        self.assertTrue(last_answer.is_correct(4))

    def test_round_trip_dictionary(self) -> None:
        """객체→dict→객체 변환 후 모든 데이터가 같은지 확인한다."""
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored, self.quiz)

    def test_old_dictionary_without_hint_uses_compatible_default(self) -> None:
        """힌트가 없던 예전 데이터도 기본 힌트로 읽을 수 있는지 확인한다."""
        restored = Quiz.from_dict(
            {
                "question": "이전 형식 문제",
                "choices": ["하나", "둘", "셋", "넷"],
                "answer": 1,
            }
        )

        self.assertEqual(restored.hint, "힌트가 없습니다.")

    def test_rejects_invalid_choice_count(self) -> None:
        """선택지가 네 개가 아니면 ValueError가 발생하는지 확인한다."""
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘"], 1)

    def test_rejects_duplicate_choices(self) -> None:
        """서로 같은 선택지를 포함한 잘못된 문제를 거부하는지 확인한다."""
        with self.assertRaises(ValueError):
            Quiz("문제", ["같음", "같음", "셋", "넷"], 1)

    def test_rejects_empty_hint(self) -> None:
        """공백뿐인 힌트를 빈 값으로 판단해 거부하는지 확인한다."""
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], 1, " ")

    def test_rejects_non_string_hint(self) -> None:
        """힌트가 문자열이 아닐 때 명확히 거부하는지 확인한다."""
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], 1, 123)

    def test_formats_question(self) -> None:
        """문제 번호와 선택지 번호가 출력 문자열에 포함되는지 확인한다."""
        rendered = self.quiz.format_question(2)
        self.assertIn("[문제 2]", rendered)
        self.assertIn("3. list", rendered)


if __name__ == "__main__":
    unittest.main()
