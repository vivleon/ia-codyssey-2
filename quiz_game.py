"""퀴즈 게임의 메뉴와 전체 실행 흐름."""

import random
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from quiz import Quiz
from storage import (
    BACKUP_LIMIT as STORAGE_BACKUP_LIMIT,
    SCHEMA_VERSION as STORAGE_SCHEMA_VERSION,
    load_state_file,
    save_state_file,
)


class QuizGame:
    """여러 퀴즈와 게임 진행을 관리한다."""

    STATE_FILE = Path(__file__).resolve().with_name("state.json")
    SCHEMA_VERSION = STORAGE_SCHEMA_VERSION
    BACKUP_LIMIT = STORAGE_BACKUP_LIMIT
    HINT_PENALTY = 10

    MENU = """
========================================
        🤖 AI 탐험 퀴즈 게임 🤖
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 퀴즈 삭제
6. 종료
========================================"""

    def __init__(
        self,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
        shuffle_func: Callable[[List[Quiz]], None] = random.shuffle,
        state_file: Optional[Path] = None,
    ) -> None:
        # 테스트에서는 input, print, random.shuffle을 다른 함수로 바꿀 수 있다.
        self.input = input_func
        self.output = output_func
        self.shuffle = shuffle_func
        self.state_file = Path(state_file) if state_file else self.STATE_FILE

        self.quizzes: List[Quiz] = []
        self.best_score: Optional[dict] = None
        self.score_history: List[dict] = []
        self.running = True

        self.load_state()

    # ------------------------------------------------------------------
    # 1. 메뉴 실행
    # ------------------------------------------------------------------
    def run(self) -> None:
        """사용자가 종료할 때까지 메뉴를 반복한다."""
        try:
            while self.running:
                self.output(self.MENU)
                menu = self._read_int("선택: ", 1, 6)

                if menu == 1:
                    self.play_quiz()
                elif menu == 2:
                    self.add_quiz()
                elif menu == 3:
                    self.list_quizzes()
                elif menu == 4:
                    self.show_best_score()
                elif menu == 5:
                    self.delete_quiz()
                else:
                    self.running = False
                    self.output("\n게임을 종료합니다. 다음에 또 만나요!")

        except (KeyboardInterrupt, EOFError):
            self.running = False
            self.output("\n입력이 중단되었습니다. 안전하게 종료합니다.")
        finally:
            # 정상 종료와 Ctrl+C 종료 모두 여기에서 저장된다.
            self.save_state()

    # ------------------------------------------------------------------
    # 2. JSON 파일 읽기와 쓰기
    # ------------------------------------------------------------------
    def load_state(self) -> None:
        """storage.py를 사용해 저장된 상태를 읽는다."""
        state = load_state_file(self.state_file, self.output)
        self.quizzes, self.best_score, self.score_history = state

    def save_state(self) -> bool:
        """storage.py를 사용해 현재 상태를 저장한다."""
        return save_state_file(
            self.state_file,
            self.quizzes,
            self.best_score,
            self.score_history,
            self.output,
        )

    # ------------------------------------------------------------------
    # 3. 사용자 입력
    # ------------------------------------------------------------------
    def _read_int(self, prompt: str, minimum: int, maximum: int) -> int:
        """범위 안의 정수를 입력할 때까지 다시 묻는다."""
        while True:
            text = self.input(prompt).strip()
            if not text:
                self.output("값을 입력해 주세요.")
                continue

            try:
                number = int(text)
            except ValueError:
                self.output("숫자로 입력해 주세요.")
                continue

            if minimum <= number <= maximum:
                return number
            self.output(f"{minimum}부터 {maximum} 사이의 숫자를 입력해 주세요.")

    def _read_text(self, prompt: str) -> str:
        """내용이 있는 문자열을 입력할 때까지 다시 묻는다."""
        while True:
            text = self.input(prompt).strip()
            if text:
                return text
            self.output("내용을 입력해 주세요.")

    def _read_answer(self, quiz: Quiz) -> tuple[int, bool]:
        """정답 번호를 받는다. h를 입력하면 힌트를 한 번 보여 준다."""
        hint_used = False

        while True:
            text = self.input("정답 입력 (1-4, 힌트 h): ").strip()

            if text.lower() == "h":
                if hint_used:
                    self.output("이 문제의 힌트는 이미 사용했습니다.")
                else:
                    hint_used = True
                    self.output(f"💡 힌트: {quiz.hint}")
                    self.output(f"최종 점수에서 {self.HINT_PENALTY}점 차감됩니다.")
                continue

            try:
                answer = int(text)
            except ValueError:
                self.output(
                    "1부터 4 사이의 숫자 또는 힌트 h를 입력해 주세요."
                )
                continue

            if 1 <= answer <= 4:
                return answer, hint_used
            self.output(
                "1부터 4 사이의 숫자 또는 힌트 h를 입력해 주세요."
            )

    # ------------------------------------------------------------------
    # 4. 퀴즈 풀기
    # ------------------------------------------------------------------
    def play_quiz(self) -> None:
        """문제 수를 고르고 퀴즈를 푼 뒤 결과를 저장한다."""
        if not self.quizzes:
            self.output(
                "\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요."
            )
            return

        questions = self._choose_questions()
        correct_count = 0
        hints_used = 0
        self.output(f"\n퀴즈를 시작합니다! (총 {len(questions)}문제)")

        for number, quiz in enumerate(questions, start=1):
            is_correct, used_hint = self._solve_one_question(quiz, number)
            if is_correct:
                correct_count += 1
            if used_hint:
                hints_used += 1

        result = self._make_result(correct_count, len(questions), hints_used)
        self._finish_game(result)

    def _choose_questions(self) -> List[Quiz]:
        """퀴즈를 섞고 사용자가 선택한 개수만 반환한다."""
        questions = list(self.quizzes)
        self.shuffle(questions)
        count = self._read_int(
            f"몇 문제를 풀까요? (1-{len(questions)}): ",
            1,
            len(questions),
        )
        return questions[:count]

    def _solve_one_question(self, quiz: Quiz, number: int) -> tuple[bool, bool]:
        """문제 한 개를 풀고 정답 여부와 힌트 사용 여부를 반환한다."""
        self.output(f"\n{quiz.format_question(number)}")
        answer, hint_used = self._read_answer(quiz)

        if quiz.is_correct(answer):
            self.output("✅ 정답입니다!")
            return True, hint_used

        correct_choice = quiz.choices[quiz.answer - 1]
        self.output(
            f"❌ 오답입니다. 정답은 {quiz.answer}번 '{correct_choice}'입니다."
        )
        return False, hint_used

    def _make_result(self, correct: int, total: int, hints: int) -> dict:
        """정답률을 계산하고 힌트 점수를 뺀다."""
        original_score = round(correct / total * 100)
        final_score = max(0, original_score - hints * self.HINT_PENALTY)
        return {
            "correct": correct,
            "total": total,
            "percentage": final_score,
            "hints_used": hints,
        }

    def _finish_game(self, result: dict) -> None:
        """결과를 출력하고 최고 점수와 히스토리를 저장한다."""
        self.output("\n" + "=" * 40)
        self.output(
            f"🏆 결과: {result['total']}문제 중 {result['correct']}문제 정답! "
            f"({result['percentage']}점)"
        )
        if result["hints_used"]:
            penalty = result["hints_used"] * self.HINT_PENALTY
            self.output(f"💡 힌트 {result['hints_used']}회: {penalty}점 차감")

        is_new_best = self._is_new_best(result)
        if is_new_best:
            self.best_score = dict(result)
            self.output("🎉 새로운 최고 점수입니다!")

        record = {"played_at": self._current_time(), **result}
        self.score_history.append(record)

        if self.save_state():
            message = "최고 점수" if is_new_best else "게임 기록"
            self.output(f"✅ {message}이 상태 파일에 저장되었습니다.")
        elif is_new_best:
            self.output(
                "⚠️ 최고 점수는 갱신되었지만 게임 기록과 함께 "
                "파일 저장에 실패했습니다."
            )
        else:
            self.output("⚠️ 게임 기록의 파일 저장에 실패했습니다.")
        self.output("=" * 40)

    @staticmethod
    def _current_time() -> str:
        """현재 날짜와 시간을 시간대와 함께 문자열로 반환한다."""
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def _is_new_best(self, result: dict) -> bool:
        """점수가 높거나, 같은 점수에서 정답 수가 많으면 최고 기록이다."""
        if self.best_score is None:
            return True

        old = (self.best_score["percentage"], self.best_score["correct"])
        new = (result["percentage"], result["correct"])
        return new > old

    # ------------------------------------------------------------------
    # 5. 퀴즈 추가, 목록, 삭제, 점수 확인
    # ------------------------------------------------------------------
    def add_quiz(self) -> None:
        """새 퀴즈를 입력받아 저장한다."""
        self.output("\n📌 새로운 퀴즈를 추가합니다.")
        question = self._read_text("문제를 입력하세요: ")
        choices: List[str] = []

        for number in range(1, 5):
            while True:
                choice = self._read_text(f"선택지 {number}: ")
                if choice in choices:
                    self.output(
                        "이미 입력한 선택지입니다. "
                        "다른 내용을 입력해 주세요."
                    )
                else:
                    choices.append(choice)
                    break

        answer = self._read_int("정답 번호 (1-4): ", 1, 4)
        hint = self._read_text("힌트를 입력하세요: ")
        self.quizzes.append(Quiz(question, choices, answer, hint))

        if self.save_state():
            self.output("✅ 퀴즈가 추가되고 저장되었습니다!")
        else:
            self.output("⚠️ 퀴즈는 추가되었지만 파일 저장에 실패했습니다.")

    def list_quizzes(self) -> None:
        """모든 퀴즈의 문제, 선택지, 정답과 힌트를 보여 준다."""
        if not self.quizzes:
            self.output("\n등록된 퀴즈가 없습니다.")
            return

        self.output(f"\n📚 저장된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            self.output(f"\n{quiz.format_question(number)}")
            self.output(f"정답: {quiz.answer}번")
            self.output(f"힌트: {quiz.hint}")

    def delete_quiz(self) -> None:
        """선택한 퀴즈를 삭제하고 저장한다."""
        if not self.quizzes:
            self.output("\n삭제할 퀴즈가 없습니다.")
            return

        self.output(f"\n🗑️ 삭제할 퀴즈를 선택하세요. (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            self.output(f"{number}. {quiz.question}")

        number = self._read_int("삭제할 퀴즈 번호: ", 1, len(self.quizzes))
        deleted = self.quizzes.pop(number - 1)

        if self.save_state():
            self.output(f"✅ '{deleted.question}' 퀴즈를 삭제하고 저장했습니다.")
        else:
            # 저장에 실패하면 삭제 전 상태로 되돌린다.
            self.quizzes.insert(number - 1, deleted)
            self.output("⚠️ 저장에 실패하여 퀴즈 삭제를 취소했습니다.")

    def show_best_score(self) -> None:
        """최고 점수와 지금까지의 모든 게임 기록을 보여 준다."""
        if self.best_score is None:
            self.output("\n아직 퀴즈를 풀지 않았습니다.")
            return

        score = self.best_score
        self.output("\n🏅 최고 점수")
        self.output(
            f"{score['total']}문제 중 {score['correct']}문제 정답 "
            f"({score['percentage']}점)"
        )

        self.output(f"\n📊 전체 게임 기록 (총 {len(self.score_history)}회)")
        for number, record in enumerate(self.score_history, start=1):
            self.output(
                f"{number}. {record['played_at']} | "
                f"{record['total']}문제 중 {record['correct']}문제 정답 | "
                f"힌트 {record['hints_used']}회 | {record['percentage']}점"
            )
