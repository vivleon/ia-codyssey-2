"""퀴즈 게임의 메뉴와 전체 실행 흐름."""

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
    ) -> None:
        self.input = input_func
        self.output = output_func
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
        """퀴즈 플레이 기능이 연결될 자리."""
        self.output("\n퀴즈 풀기 기능을 준비하고 있습니다.")

    def add_quiz(self) -> None:
        """퀴즈 등록 기능이 연결될 자리."""
        self.output("\n퀴즈 추가 기능을 준비하고 있습니다.")

    def list_quizzes(self) -> None:
        """퀴즈 목록 기능이 연결될 자리."""
        self.output("\n퀴즈 목록 기능을 준비하고 있습니다.")

    def show_best_score(self) -> None:
        """점수 확인 기능이 연결될 자리."""
        self.output("\n점수 확인 기능을 준비하고 있습니다.")

