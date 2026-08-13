"""Quiz 모델 단위 테스트."""

import unittest

from quiz import Quiz


class QuizTest(unittest.TestCase):
    def setUp(self) -> None:
        self.quiz = Quiz(
            "Python에서 목록을 표현하는 자료형은?",
            ["int", "str", "list", "bool"],
            3,
            "대괄호를 사용하는 자료형입니다.",
        )

    def test_checks_answer(self) -> None:
        self.assertTrue(self.quiz.is_correct(3))
        self.assertFalse(self.quiz.is_correct(1))

    def test_accepts_first_and_last_answer_boundaries(self) -> None:
        choices = ["하나", "둘", "셋", "넷"]
        first_answer = Quiz("첫 번째가 정답인 문제", choices, 1)
        last_answer = Quiz("마지막이 정답인 문제", choices, 4)

        self.assertTrue(first_answer.is_correct(1))
        self.assertTrue(last_answer.is_correct(4))

    def test_round_trip_dictionary(self) -> None:
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored, self.quiz)

    def test_old_dictionary_without_hint_uses_compatible_default(self) -> None:
        restored = Quiz.from_dict(
            {
                "question": "이전 형식 문제",
                "choices": ["하나", "둘", "셋", "넷"],
                "answer": 1,
            }
        )

        self.assertEqual(restored.hint, "힌트가 없습니다.")

    def test_rejects_invalid_choice_count(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘"], 1)

    def test_rejects_duplicate_choices(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("문제", ["같음", "같음", "셋", "넷"], 1)

    def test_rejects_empty_hint(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], 1, " ")

    def test_rejects_non_string_hint(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], 1, 123)

    def test_formats_question(self) -> None:
        rendered = self.quiz.format_question(2)
        self.assertIn("[문제 2]", rendered)
        self.assertIn("3. list", rendered)


if __name__ == "__main__":
    unittest.main()
