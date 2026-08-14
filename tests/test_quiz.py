"""Quiz 클래스 테스트"""

import unittest
from unittest.mock import patch

from quiz import Quiz


class QuizTest(unittest.TestCase):
    def make_quiz(self):
        return Quiz(
            "Python의 리스트 기호는?",
            ["[]", "{}", "()", "<>"],
            1,
            "대괄호를 찾으세요.",
        )

    def test_answer(self):
        # 정답 번호만 True가 되어야 한다.
        quiz = self.make_quiz()

        self.assertTrue(quiz.is_correct(1))
        self.assertFalse(quiz.is_correct(2))

    def test_dict_change(self):
        # Quiz -> dict -> Quiz로 바꿔도 내용이 같아야 한다.
        quiz = self.make_quiz()
        restored = Quiz.from_dict(quiz.to_dict())

        self.assertEqual(restored.question, quiz.question)
        self.assertEqual(restored.choices, quiz.choices)
        self.assertEqual(restored.answer, quiz.answer)
        self.assertEqual(restored.hint, quiz.hint)

    def test_show(self):
        # 문제와 선택지 번호가 화면에 나오는지 확인한다.
        quiz = self.make_quiz()

        with patch("builtins.print") as fake_print:
            quiz.show(1)

        fake_print.assert_any_call("[문제", 1, "]")
        fake_print.assert_any_call("1.", "[]")

    def test_wrong_quiz_is_rejected(self):
        # 선택지가 4개가 아니면 Quiz를 만들 수 없다.
        with self.assertRaises(ValueError):
            Quiz("문제", ["1", "2"], 1)


if __name__ == "__main__":
    unittest.main()
