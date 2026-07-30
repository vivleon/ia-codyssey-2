"""퀴즈 게임의 메뉴와 전체 실행 흐름."""

import random
from typing import Callable, List, Optional

from defaults import build_default_quizzes
from quiz import Quiz


class QuizGame:
    """퀴즈 목록, 점수, 사용자 입력 흐름을 관리한다."""

    MENU = """
========================================
        🤖 AI 탐험 퀴즈 게임 🤖
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
========================================"""

    def __init__(
        self,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
        shuffle_func: Callable[[List[Quiz]], None] = random.shuffle,
    ) -> None:
        self.input = input_func
        self.output = output_func
        self.shuffle = shuffle_func
        self.quizzes: List[Quiz] = build_default_quizzes()
        self.best_score: Optional[dict] = None
        self.running = True

    def run(self) -> None:
        """메뉴를 반복하고 인터럽트 시 안전하게 종료한다."""
        actions = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.list_quizzes,
            4: self.show_best_score,
        }

        try:
            while self.running:
                self.output(self.MENU)
                selection = self._read_int("선택: ", 1, 5)
                if selection == 5:
                    self.running = False
                    self.output("\n게임을 종료합니다. 다음에 또 만나요!")
                    continue
                actions[selection]()
        except (KeyboardInterrupt, EOFError):
            self.running = False
            self.output("\n입력이 중단되었습니다. 안전하게 종료합니다.")

    def _read_int(self, prompt: str, minimum: int, maximum: int) -> int:
        """범위 안의 정수를 입력할 때까지 안내하고 다시 묻는다."""
        while True:
            raw_value = self.input(prompt).strip()
            if not raw_value:
                self.output("값을 입력해 주세요.")
                continue
            try:
                value = int(raw_value)
            except ValueError:
                self.output("숫자로 입력해 주세요.")
                continue
            if not minimum <= value <= maximum:
                self.output(f"{minimum}부터 {maximum} 사이의 숫자를 입력해 주세요.")
                continue
            return value

    def play_quiz(self) -> None:
        """모든 퀴즈를 무작위 순서로 출제하고 최고 점수를 갱신한다."""
        if not self.quizzes:
            self.output("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        questions = list(self.quizzes)
        self.shuffle(questions)
        correct_count = 0
        self.output(f"\n퀴즈를 시작합니다! (총 {len(questions)}문제)")

        for number, quiz in enumerate(questions, start=1):
            self.output(f"\n{quiz.format_question(number)}")
            selected = self._read_int("정답 입력 (1-4): ", 1, 4)
            if quiz.is_correct(selected):
                correct_count += 1
                self.output("✅ 정답입니다!")
            else:
                correct_choice = quiz.choices[quiz.answer - 1]
                self.output(
                    f"❌ 오답입니다. 정답은 {quiz.answer}번 "
                    f"'{correct_choice}'입니다."
                )

        total = len(questions)
        percentage = round(correct_count / total * 100)
        self.output("\n" + "=" * 40)
        self.output(
            f"🏆 결과: {total}문제 중 {correct_count}문제 정답! "
            f"({percentage}점)"
        )

        candidate = {
            "correct": correct_count,
            "total": total,
            "percentage": percentage,
        }
        if self._is_new_best(candidate):
            self.best_score = candidate
            self.output("🎉 새로운 최고 점수입니다!")
        self.output("=" * 40)

    def _is_new_best(self, candidate: dict) -> bool:
        """정답률을 우선하고 동률이면 정답 수로 최고 기록을 비교한다."""
        if self.best_score is None:
            return True
        current_key = (
            self.best_score.get("percentage", 0),
            self.best_score.get("correct", 0),
        )
        candidate_key = (candidate["percentage"], candidate["correct"])
        return candidate_key > current_key

    def add_quiz(self) -> None:
        """퀴즈 등록 기능이 연결될 자리."""
        self.output("\n퀴즈 추가 기능을 준비하고 있습니다.")

    def list_quizzes(self) -> None:
        """퀴즈 목록 기능이 연결될 자리."""
        self.output("\n퀴즈 목록 기능을 준비하고 있습니다.")

    def show_best_score(self) -> None:
        """점수 확인 기능이 연결될 자리."""
        self.output("\n점수 확인 기능을 준비하고 있습니다.")
