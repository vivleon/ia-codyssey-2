"""퀴즈 게임의 메뉴와 전체 실행 흐름."""

import json
import random
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from defaults import build_default_quizzes
from quiz import Quiz


class QuizGame:
    """퀴즈 목록, 점수, 사용자 입력 흐름을 관리한다."""

    STATE_FILE = Path(__file__).resolve().with_name("state.json")
    BACKUP_LIMIT = 3
    SCHEMA_VERSION = 2
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
        self.input = input_func
        self.output = output_func
        self.shuffle = shuffle_func
        self.state_file = Path(state_file) if state_file else self.STATE_FILE
        self.quizzes: List[Quiz] = []
        self.best_score: Optional[dict] = None
        self.score_history: List[dict] = []
        self.running = True
        self.load_state()

    def run(self) -> None:
        """메뉴를 반복하고 인터럽트 시 안전하게 종료한다."""
        actions = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.list_quizzes,
            4: self.show_best_score,
            5: self.delete_quiz,
        }

        try:
            while self.running:
                self.output(self.MENU)
                selection = self._read_int("선택: ", 1, 6)
                if selection == 6:
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
            self.score_history = []
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as state_handle:
                data = json.load(state_handle)
            if not isinstance(data, dict):
                raise ValueError("최상위 데이터는 객체여야 합니다.")
            schema_version = data.get("schema_version", 1)
            if (
                isinstance(schema_version, bool)
                or not isinstance(schema_version, int)
                or schema_version not in (1, self.SCHEMA_VERSION)
            ):
                raise ValueError("지원하지 않는 상태 파일 버전입니다.")
            raw_quizzes = data.get("quizzes")
            if not isinstance(raw_quizzes, list):
                raise ValueError("quizzes는 목록이어야 합니다.")
            self.quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
            self.best_score = self._validate_best_score(data.get("best_score"))
            self.score_history = self._validate_score_history(
                data.get("score_history", [])
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            self.output(
                f"상태 파일을 읽을 수 없어 기본 데이터로 복구합니다: {error}"
            )
            backup_path = self._backup_invalid_state()
            if backup_path is not None:
                self.output(f"기존 상태 파일 백업: {backup_path}")
            self.quizzes = build_default_quizzes()
            self.best_score = None
            self.score_history = []
            self.save_state()

    def _backup_invalid_state(self) -> Optional[Path]:
        """복구 전에 잘못된 상태 파일을 최대 세 개까지 보관한다."""
        if not self.state_file.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_path = self.state_file.with_name(
            f"{self.state_file.name}.broken-{timestamp}.bak"
        )
        try:
            shutil.copy2(self.state_file, backup_path)
        except OSError as error:
            self.output(f"기존 상태 파일을 백업하지 못했습니다: {error}")
            return None

        backup_pattern = f"{self.state_file.name}.broken-*.bak"
        backups = sorted(
            self.state_file.parent.glob(backup_pattern),
            reverse=True,
        )
        for expired_backup in backups[self.BACKUP_LIMIT :]:
            try:
                expired_backup.unlink()
            except OSError as error:
                self.output(f"오래된 상태 백업을 정리하지 못했습니다: {error}")
        return backup_path

    def save_state(self) -> bool:
        """퀴즈, 최고 점수와 기록을 UTF-8 JSON 파일에 원자적으로 저장한다."""
        data = {
            "schema_version": self.SCHEMA_VERSION,
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "score_history": self.score_history,
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
            self.output(f"저장 대상: {self.state_file}")
            self.output(
                f"임시 파일이 남아 있다면 내용을 확인하세요: {temporary_file}"
            )
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
        validated = {
            "correct": correct,
            "total": total,
            "percentage": percentage,
        }
        hints_used = value.get("hints_used")
        if hints_used is not None:
            if (
                isinstance(hints_used, bool)
                or not isinstance(hints_used, int)
                or not 0 <= hints_used <= total
            ):
                raise ValueError(
                    "최고 점수의 힌트 사용 횟수가 올바르지 않습니다."
                )
            validated["hints_used"] = hints_used
        return validated

    @staticmethod
    def _validate_score_history(value: object) -> List[dict]:
        """저장된 모든 게임 기록의 스키마를 검사한다."""
        if not isinstance(value, list):
            raise ValueError("score_history는 목록이어야 합니다.")

        validated_history = []
        for record in value:
            if not isinstance(record, dict):
                raise ValueError("게임 기록은 객체여야 합니다.")
            played_at = record.get("played_at")
            correct = record.get("correct")
            total = record.get("total")
            hints_used = record.get("hints_used", 0)
            percentage = record.get("percentage")
            numeric_values = (correct, total, hints_used, percentage)
            if not isinstance(played_at, str):
                raise ValueError("게임 기록 시간은 문자열이어야 합니다.")
            try:
                parsed_time = datetime.fromisoformat(played_at)
            except ValueError as error:
                raise ValueError("게임 기록 시간이 올바르지 않습니다.") from error
            if parsed_time.tzinfo is None:
                raise ValueError("게임 기록 시간에는 시간대가 필요합니다.")
            if any(
                isinstance(item, bool) or not isinstance(item, int)
                for item in numeric_values
            ):
                raise ValueError("게임 기록의 점수 값은 정수여야 합니다.")
            if (
                total <= 0
                or not 0 <= correct <= total
                or not 0 <= hints_used <= total
                or not 0 <= percentage <= 100
            ):
                raise ValueError("게임 기록의 점수 범위가 올바르지 않습니다.")
            validated_history.append(
                {
                    "played_at": played_at,
                    "correct": correct,
                    "total": total,
                    "hints_used": hints_used,
                    "percentage": percentage,
                }
            )
        return validated_history

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

    def _read_answer_with_hint(self, quiz: Quiz) -> tuple[int, bool]:
        """1~4 정답 또는 h를 받고, 한 문제에서 힌트를 한 번만 제공한다."""
        hint_used = False
        while True:
            raw_value = self.input("정답 입력 (1-4, 힌트 h): ").strip()
            if raw_value.lower() == "h":
                if hint_used:
                    self.output("이 문제의 힌트는 이미 사용했습니다.")
                else:
                    hint_used = True
                    self.output(f"💡 힌트: {quiz.hint}")
                    self.output(
                        "힌트 사용으로 최종 점수에서 "
                        f"{self.HINT_PENALTY}점 차감됩니다."
                    )
                continue
            if not raw_value:
                self.output("값을 입력해 주세요.")
                continue
            try:
                selected = int(raw_value)
            except ValueError:
                self.output("1부터 4 사이의 숫자 또는 힌트 h를 입력해 주세요.")
                continue
            if not 1 <= selected <= 4:
                self.output("1부터 4 사이의 숫자 또는 힌트 h를 입력해 주세요.")
                continue
            return selected, hint_used

    def play_quiz(self) -> None:
        """선택한 수의 퀴즈를 무작위 출제하고 점수와 기록을 저장한다."""
        if not self.quizzes:
            self.output(
                "\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요."
            )
            return

        questions = list(self.quizzes)
        self.shuffle(questions)
        question_count = self._read_int(
            f"몇 문제를 풀까요? (1-{len(questions)}): ",
            1,
            len(questions),
        )
        questions = questions[:question_count]
        correct_count = 0
        hints_used = 0
        self.output(f"\n퀴즈를 시작합니다! (총 {len(questions)}문제)")

        for number, quiz in enumerate(questions, start=1):
            self.output(f"\n{quiz.format_question(number)}")
            selected, used_hint = self._read_answer_with_hint(quiz)
            if used_hint:
                hints_used += 1
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
        raw_percentage = round(correct_count / total * 100)
        percentage = max(0, raw_percentage - hints_used * self.HINT_PENALTY)
        self.output("\n" + "=" * 40)
        self.output(
            f"🏆 결과: {total}문제 중 {correct_count}문제 정답! "
            f"({percentage}점)"
        )
        if hints_used:
            self.output(
                f"💡 힌트 {hints_used}회: {raw_percentage}점에서 "
                f"{hints_used * self.HINT_PENALTY}점 차감"
            )

        candidate = {
            "correct": correct_count,
            "total": total,
            "percentage": percentage,
            "hints_used": hints_used,
        }
        is_new_best = self._is_new_best(candidate)
        if is_new_best:
            self.best_score = candidate
            self.output("🎉 새로운 최고 점수입니다!")
        self.score_history.append(
            {
                "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "correct": correct_count,
                "total": total,
                "hints_used": hints_used,
                "percentage": percentage,
            }
        )
        if self.save_state():
            if is_new_best:
                self.output("✅ 최고 점수가 상태 파일에 저장되었습니다.")
            else:
                self.output("✅ 게임 기록이 상태 파일에 저장되었습니다.")
        elif is_new_best:
            self.output(
                "⚠️ 최고 점수는 갱신되었지만 게임 기록과 함께 "
                "파일 저장에 실패했습니다."
            )
        else:
            self.output("⚠️ 게임 기록의 파일 저장에 실패했습니다.")
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
                    self.output(
                        "이미 입력한 선택지입니다. "
                        "다른 내용을 입력해 주세요."
                    )
                    continue
                choices.append(choice)
                break

        answer = self._read_int("정답 번호 (1-4): ", 1, 4)
        hint = self._read_non_empty("힌트를 입력하세요: ")
        self.quizzes.append(Quiz(question, choices, answer, hint))
        if self.save_state():
            self.output("✅ 퀴즈가 추가되고 저장되었습니다!")
        else:
            self.output("⚠️ 퀴즈는 추가되었지만 파일 저장에 실패했습니다.")

    def list_quizzes(self) -> None:
        """저장된 문제와 선택지, 정답을 순서대로 보여 준다."""
        if not self.quizzes:
            self.output("\n등록된 퀴즈가 없습니다.")
            return

        self.output(f"\n📚 저장된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            self.output(f"\n{quiz.format_question(number)}")
            self.output(f"정답: {quiz.answer}번")
            self.output(f"힌트: {quiz.hint}")

    def delete_quiz(self) -> None:
        """선택한 퀴즈를 삭제하고 상태 파일에 즉시 반영한다."""
        if not self.quizzes:
            self.output("\n삭제할 퀴즈가 없습니다.")
            return

        self.output(f"\n🗑️ 삭제할 퀴즈를 선택하세요. (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            self.output(f"{number}. {quiz.question}")
        selected = self._read_int("삭제할 퀴즈 번호: ", 1, len(self.quizzes))
        deleted_quiz = self.quizzes.pop(selected - 1)
        if self.save_state():
            self.output(
                f"✅ '{deleted_quiz.question}' 퀴즈를 삭제하고 저장했습니다."
            )
        else:
            self.quizzes.insert(selected - 1, deleted_quiz)
            self.output("⚠️ 저장에 실패하여 퀴즈 삭제를 취소했습니다.")

    def show_best_score(self) -> None:
        """현재 최고 점수와 모든 게임 기록을 보여 준다."""
        if self.best_score is None:
            self.output("\n아직 퀴즈를 풀지 않았습니다.")
            return

        self.output("\n🏅 최고 점수")
        self.output(
            f"{self.best_score['total']}문제 중 "
            f"{self.best_score['correct']}문제 정답 "
            f"({self.best_score['percentage']}점)"
        )
        self.output(f"\n📊 전체 게임 기록 (총 {len(self.score_history)}회)")
        for number, record in enumerate(self.score_history, start=1):
            self.output(
                f"{number}. {record['played_at']} | "
                f"{record['total']}문제 중 {record['correct']}문제 정답 | "
                f"힌트 {record['hints_used']}회 | {record['percentage']}점"
            )
