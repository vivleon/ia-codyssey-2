"""퀴즈 게임의 메뉴와 전체 실행 흐름."""

import json
import random
from pathlib import Path
from typing import Callable, List, Optional

from defaults import build_default_quizzes
from quiz import Quiz


class QuizGame:
    """퀴즈 목록, 점수, 사용자 입력 흐름을 관리한다."""

    STATE_FILE = Path(__file__).resolve().with_name("state.json")

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
        state_file: Optional[Path] = None,
    ) -> None:
        self.input = input_func
        self.output = output_func
        self.shuffle = shuffle_func
        self.state_file = Path(state_file) if state_file else self.STATE_FILE
        self.quizzes: List[Quiz] = []
        self.best_score: Optional[dict] = None
        self.running = True
        self.load_state()

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
        finally:
            self.save_state()

    def load_state(self) -> None:
        """state.json을 읽고, 없거나 손상되면 기본 데이터로 복구한다."""
        if not self.state_file.exists():
            self.quizzes = build_default_quizzes()
            self.best_score = None
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as state_handle:
                data = json.load(state_handle)
            if not isinstance(data, dict):
                raise ValueError("최상위 데이터는 객체여야 합니다.")
            raw_quizzes = data.get("quizzes")
            if not isinstance(raw_quizzes, list):
                raise ValueError("quizzes는 목록이어야 합니다.")
            self.quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
            self.best_score = self._validate_best_score(data.get("best_score"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            self.output(
                f"상태 파일을 읽을 수 없어 기본 데이터로 복구합니다: {error}"
            )
            self.quizzes = build_default_quizzes()
            self.best_score = None
            self.save_state()

    def save_state(self) -> bool:
        """현재 퀴즈와 최고 점수를 UTF-8 JSON 파일에 원자적으로 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        temporary_file = self.state_file.with_name(f".{self.state_file.name}.tmp")
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with temporary_file.open("w", encoding="utf-8") as state_handle:
                json.dump(data, state_handle, ensure_ascii=False, indent=2)
                state_handle.write("\n")
            temporary_file.replace(self.state_file)
            return True
        except OSError as error:
            self.output(f"상태 파일을 저장하지 못했습니다: {error}")
            return False

    @staticmethod
    def _validate_best_score(value: object) -> Optional[dict]:
        """저장된 최고 점수 스키마를 검사한다."""
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("best_score는 객체 또는 null이어야 합니다.")

        correct = value.get("correct")
        total = value.get("total")
        percentage = value.get("percentage")
        score_values = (correct, total, percentage)
        if any(isinstance(item, bool) or not isinstance(item, int) for item in score_values):
            raise ValueError("최고 점수 값은 정수여야 합니다.")
        if total <= 0 or not 0 <= correct <= total or not 0 <= percentage <= 100:
            raise ValueError("최고 점수 값의 범위가 올바르지 않습니다.")
        return {
            "correct": correct,
            "total": total,
            "percentage": percentage,
        }

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

    def _read_non_empty(self, prompt: str) -> str:
        """공백이 아닌 문자열을 입력할 때까지 다시 묻는다."""
        while True:
            value = self.input(prompt).strip()
            if value:
                return value
            self.output("내용을 입력해 주세요.")

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
            self.save_state()
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
        """문제, 선택지 네 개, 정답 번호를 입력받아 저장한다."""
        self.output("\n📌 새로운 퀴즈를 추가합니다.")
        question = self._read_non_empty("문제를 입력하세요: ")
        choices: List[str] = []

        for number in range(1, 5):
            while True:
                choice = self._read_non_empty(f"선택지 {number}: ")
                if choice in choices:
                    self.output("이미 입력한 선택지입니다. 다른 내용을 입력해 주세요.")
                    continue
                choices.append(choice)
                break

        answer = self._read_int("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            self.output("✅ 퀴즈가 추가되고 저장되었습니다!")
        else:
            self.output("⚠️ 퀴즈는 추가되었지만 파일 저장에 실패했습니다.")

    def list_quizzes(self) -> None:
        """퀴즈 목록 기능이 연결될 자리."""
        self.output("\n퀴즈 목록 기능을 준비하고 있습니다.")

    def show_best_score(self) -> None:
        """점수 확인 기능이 연결될 자리."""
        self.output("\n점수 확인 기능을 준비하고 있습니다.")
