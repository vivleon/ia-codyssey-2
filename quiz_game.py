"""퀴즈 게임의 메뉴, 사용자 입력, 게임 진행을 담당하는 파일.

코드를 읽을 때는 ``run()``에서 시작해 선택한 메뉴의 메서드로 이동하면 된다.
JSON의 세부 처리는 ``storage.py``, 문제 한 개의 규칙은 ``quiz.py``에 맡겨
이 파일이 지나치게 복잡해지지 않도록 책임을 나눴다.
"""

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
    """여러 퀴즈, 점수, 메뉴 실행을 하나로 관리하는 게임 객체.

    클래스 속성은 모든 게임 객체가 함께 사용하는 설정값이고, ``self``로
    시작하는 인스턴스 속성은 현재 게임 객체가 가진 상태이다. 따라서 테스트용
    게임과 실제 게임을 각각 만들어도 퀴즈 목록과 점수는 서로 섞이지 않는다.
    """

    # __file__은 현재 Python 파일의 경로다. 실행 위치가 달라도 이 파일 옆의
    # state.json을 찾도록 절대 경로로 바꾼 뒤 파일 이름만 교체한다.
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
        """필요한 도구와 초기 상태를 준비한 뒤 저장 데이터를 불러온다.

        기본값은 실제 ``input``, ``print``, ``random.shuffle``이다. 테스트에서는
        미리 준비한 가짜 함수로 바꿔 키보드 입력 없이 같은 상황을 재현할 수 있다.
        이런 방식을 의존성 주입이라고 하며, 기능 자체와 외부 환경을 분리한다.
        """
        # 전달받은 함수를 self에 저장하면 다른 메서드에서도 동일하게 사용할 수 있다.
        self.input = input_func
        self.output = output_func
        self.shuffle = shuffle_func
        self.state_file = Path(state_file) if state_file else self.STATE_FILE

        # 아래 세 값은 실행 중 메모리에 존재하는 게임 상태이다.
        self.quizzes: List[Quiz] = []
        self.best_score: Optional[dict] = None
        self.score_history: List[dict] = []
        self.running = True

        self.load_state()

    # ------------------------------------------------------------------
    # 1. 메뉴 실행
    # ------------------------------------------------------------------
    def run(self) -> None:
        """사용자가 종료를 고를 때까지 메뉴를 반복하고 기능을 연결한다.

        ``while``은 반복 횟수가 아니라 ``self.running``이라는 종료 조건이
        중요할 때 적합하다. ``if/elif/else``는 입력된 번호에 맞는 메서드 하나만
        실행한다. 예외가 생겨도 ``finally``는 반드시 실행되어 상태를 저장한다.
        """
        try:
            while self.running:
                self.output(self.MENU)
                menu = self._read_int("선택: ", 1, 6)

                # 각 메뉴는 별도 메서드로 분리되어 있어 수정 위치가 명확하다.
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

        # Ctrl+C는 KeyboardInterrupt, 입력 스트림 종료는 EOFError를 발생시킨다.
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
        """storage.py에서 읽은 세 값을 현재 게임 객체에 저장한다.

        여러 값을 한 번에 대입하는 Python의 튜플 언패킹을 사용한다.
        """
        state = load_state_file(self.state_file, self.output)
        self.quizzes, self.best_score, self.score_history = state

    def save_state(self) -> bool:
        """현재 상태를 storage.py에 전달하고 저장 성공 여부를 반환한다.

        반환값이 bool이므로 호출한 메서드는 성공/실패에 맞는 안내를 할 수 있다.
        """
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
        """최솟값과 최댓값 사이의 정수를 입력할 때까지 다시 묻는다.

        입력은 항상 str이므로 ``int()``로 변환한다. 변환할 수 없을 때 발생하는
        ValueError만 처리해 빈 값, 문자, 범위 밖 숫자에 각각 정확한 안내를 한다.
        """
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
        """공백을 제외한 내용이 있는 문자열을 받을 때까지 반복한다."""
        while True:
            text = self.input(prompt).strip()
            if text:
                return text
            self.output("내용을 입력해 주세요.")

    def _read_answer(self, quiz: Quiz) -> tuple[int, bool]:
        """정답 번호와 힌트 사용 여부를 함께 반환한다.

        반환값 ``(answer, hint_used)``는 두 값을 묶은 튜플이다. 한 문제에서
        힌트를 여러 번 요청해도 한 번만 보여 주고 감점도 한 번만 적용한다.
        """
        hint_used = False

        while True:
            text = self.input("정답 입력 (1-4, 힌트 h): ").strip()

            # lower()를 사용하므로 사용자가 H 또는 h 중 무엇을 입력해도 된다.
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
        """문제 선택 → 반복 출제 → 점수 계산 → 기록 저장 순서로 진행한다.

        각 단계를 작은 메서드로 나눠, 한 단계의 규칙을 바꿔도 다른 단계에
        미치는 영향을 줄였다.
        """
        if not self.quizzes:
            self.output(
                "\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요."
            )
            return

        questions = self._choose_questions()
        correct_count = 0
        hints_used = 0
        self.output(f"\n퀴즈를 시작합니다! (총 {len(questions)}문제)")

        # for는 풀 문제 목록이 이미 정해졌을 때 각 항목을 한 번씩 처리하기 좋다.
        for number, quiz in enumerate(questions, start=1):
            is_correct, used_hint = self._solve_one_question(quiz, number)
            if is_correct:
                correct_count += 1
            if used_hint:
                hints_used += 1

        result = self._make_result(correct_count, len(questions), hints_used)
        self._finish_game(result)

    def _choose_questions(self) -> List[Quiz]:
        """전체 퀴즈의 복사본을 무작위로 섞고 선택한 개수만 반환한다.

        원본 ``self.quizzes``를 바로 섞으면 목록 메뉴의 저장 순서까지 변한다.
        ``list(...)``로 얕은 복사본을 만든 뒤 섞어 출제 순서만 바꾼다.
        리스트 슬라이싱 ``[:count]``은 앞에서 count개를 선택한다.
        """
        questions = list(self.quizzes)
        self.shuffle(questions)
        count = self._read_int(
            f"몇 문제를 풀까요? (1-{len(questions)}): ",
            1,
            len(questions),
        )
        return questions[:count]

    def _solve_one_question(self, quiz: Quiz, number: int) -> tuple[bool, bool]:
        """문제 하나를 출력하고 ``(정답 여부, 힌트 사용 여부)``를 반환한다."""
        self.output(f"\n{quiz.format_question(number)}")
        answer, hint_used = self._read_answer(quiz)

        if quiz.is_correct(answer):
            self.output("✅ 정답입니다!")
            return True, hint_used

        # 화면의 정답 번호는 1부터, 리스트 index는 0부터 시작하므로 1을 뺀다.
        correct_choice = quiz.choices[quiz.answer - 1]
        self.output(
            f"❌ 오답입니다. 정답은 {quiz.answer}번 '{correct_choice}'입니다."
        )
        return False, hint_used

    def _make_result(self, correct: int, total: int, hints: int) -> dict:
        """100점 기준 정답률에서 힌트 감점을 빼 결과 dict를 만든다.

        ``round``는 정답률을 정수 점수로 반올림한다. ``max(0, ...)``은 힌트를
        많이 써도 최종 점수가 0보다 작아지지 않도록 하한선을 만든다.
        """
        original_score = round(correct / total * 100)
        final_score = max(0, original_score - hints * self.HINT_PENALTY)
        return {
            "correct": correct,
            "total": total,
            "percentage": final_score,
            "hints_used": hints,
        }

    def _finish_game(self, result: dict) -> None:
        """결과를 안내하고 최고 기록·전체 기록을 갱신한 뒤 저장한다.

        최고 점수는 대표 기록 하나이며, score_history에는 매 게임 결과를
        빠짐없이 append한다. 두 데이터를 한 번의 save_state()로 함께 저장하면
        파일 내용이 서로 다른 시점의 상태가 되는 문제를 줄일 수 있다.
        """
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

        # **result는 result dict의 필드를 새 dict 안에 펼치는 문법이다.
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
        """현재 시각을 시간대가 포함된 ISO 8601 문자열로 반환한다.

        표준 형식이라 사람이 읽을 수 있고 ``datetime.fromisoformat``으로
        다시 해석할 수도 있다. 시간대를 포함해 실행 지역도 구분한다.
        """
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def _is_new_best(self, result: dict) -> bool:
        """점수가 높거나 같은 점수에서 정답 수가 많으면 True를 반환한다.

        Python은 튜플을 왼쪽 값부터 비교한다. 따라서 먼저 percentage를 비교하고,
        같을 때만 correct를 비교하는 규칙을 간단하게 표현할 수 있다.
        """
        if self.best_score is None:
            return True

        old = (self.best_score["percentage"], self.best_score["correct"])
        new = (result["percentage"], result["correct"])
        return new > old

    # ------------------------------------------------------------------
    # 5. 퀴즈 추가, 목록, 삭제, 점수 확인
    # ------------------------------------------------------------------
    def add_quiz(self) -> None:
        """질문·선택지·정답·힌트를 입력받아 Quiz 객체로 만들고 저장한다."""
        self.output("\n📌 새로운 퀴즈를 추가합니다.")
        question = self._read_text("문제를 입력하세요: ")
        choices: List[str] = []

        # 선택지는 항상 네 개이므로 1, 2, 3, 4를 만드는 range를 사용한다.
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
        # Quiz 생성 시 __post_init__ 검증도 자동으로 실행된다.
        self.quizzes.append(Quiz(question, choices, answer, hint))

        if self.save_state():
            self.output("✅ 퀴즈가 추가되고 저장되었습니다!")
        else:
            self.output("⚠️ 퀴즈는 추가되었지만 파일 저장에 실패했습니다.")

    def list_quizzes(self) -> None:
        """등록된 Quiz 객체를 순서대로 읽어 문제·정답·힌트를 보여 준다."""
        if not self.quizzes:
            self.output("\n등록된 퀴즈가 없습니다.")
            return

        self.output(f"\n📚 저장된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            self.output(f"\n{quiz.format_question(number)}")
            self.output(f"정답: {quiz.answer}번")
            self.output(f"힌트: {quiz.hint}")

    def delete_quiz(self) -> None:
        """선택한 퀴즈를 삭제하고, 저장 실패 시 메모리 상태를 복원한다.

        파일에 반영되지 않았는데 화면에서만 사라지는 불일치를 막기 위해
        삭제된 객체를 잠시 보관했다가 실패하면 원래 index에 다시 insert한다.
        """
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
        """최고 점수와 날짜별 전체 게임 기록을 읽기 쉬운 형태로 출력한다."""
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
