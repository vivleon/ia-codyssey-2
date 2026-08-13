"""state.json 읽기와 쓰기.

게임 흐름을 처음 공부할 때는 이 파일을 나중에 읽어도 됩니다.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from defaults import build_default_quizzes
from quiz import Quiz


SCHEMA_VERSION = 2
BACKUP_LIMIT = 3
OutputFunction = Callable[[str], None]
GameState = Tuple[List[Quiz], Optional[dict], List[dict]]


def load_state_file(path: Path, output: OutputFunction) -> GameState:
    """JSON 파일을 읽고 퀴즈, 최고 점수, 게임 기록을 반환한다."""
    if not path.exists():
        return default_state()

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return parse_state(data)

    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        output(f"상태 파일을 읽을 수 없어 기본 데이터로 복구합니다: {error}")
        backup = backup_broken_file(path, output)
        if backup:
            output(f"기존 상태 파일 백업: {backup}")

        quizzes, best_score, history = default_state()
        save_state_file(path, quizzes, best_score, history, output)
        return quizzes, best_score, history


def default_state() -> GameState:
    """기본 퀴즈 18개와 빈 점수를 만든다."""
    return build_default_quizzes(), None, []


def parse_state(data: object) -> GameState:
    """JSON에서 읽은 값의 기본 구조를 확인한다."""
    if not isinstance(data, dict):
        raise ValueError("최상위 데이터는 객체여야 합니다.")

    version = data.get("schema_version", 1)
    quizzes = data.get("quizzes")
    history = data.get("score_history", [])

    if type(version) is not int or version not in (1, SCHEMA_VERSION):
        raise ValueError("지원하지 않는 상태 파일 버전입니다.")
    if not isinstance(quizzes, list):
        raise ValueError("quizzes는 목록이어야 합니다.")
    if not isinstance(history, list):
        raise ValueError("score_history는 목록이어야 합니다.")

    quiz_objects = [Quiz.from_dict(item) for item in quizzes]
    best_score = validate_best_score(data.get("best_score"))
    records = [validate_record(item) for item in history]
    return quiz_objects, best_score, records


def save_state_file(
    path: Path,
    quizzes: List[Quiz],
    best_score: Optional[dict],
    history: List[dict],
    output: OutputFunction,
) -> bool:
    """임시 파일을 완성한 뒤 state.json으로 교체한다."""
    data = {
        "schema_version": SCHEMA_VERSION,
        "quizzes": [quiz.to_dict() for quiz in quizzes],
        "best_score": best_score,
        "score_history": history,
    }
    temporary_file = path.with_name(f".{path.name}.tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_file.replace(path)
        return True
    except OSError as error:
        output(f"상태 파일을 저장하지 못했습니다: {error}")
        output(f"저장 대상: {path}")
        output(f"임시 파일이 남아 있다면 확인하세요: {temporary_file}")
        return False


def validate_best_score(score: object) -> Optional[dict]:
    """최고 점수를 확인한다. 이전 형식에는 hints_used가 없을 수 있다."""
    if score is None:
        return None
    if not isinstance(score, dict):
        raise ValueError("best_score는 객체 또는 null이어야 합니다.")

    check_score_numbers(score)
    result = {
        "correct": score["correct"],
        "total": score["total"],
        "percentage": score["percentage"],
    }
    if "hints_used" in score:
        result["hints_used"] = score["hints_used"]
    return result


def validate_record(record: object) -> dict:
    """게임 기록의 점수와 날짜를 확인한다."""
    if not isinstance(record, dict):
        raise ValueError("게임 기록은 객체여야 합니다.")

    check_score_numbers(record)
    played_at = record.get("played_at")
    if not isinstance(played_at, str):
        raise ValueError("게임 기록 시간은 문자열이어야 합니다.")

    try:
        parsed_time = datetime.fromisoformat(played_at)
    except ValueError as error:
        raise ValueError("게임 기록 시간이 올바르지 않습니다.") from error
    if parsed_time.tzinfo is None:
        raise ValueError("게임 기록 시간에는 시간대가 필요합니다.")

    return {
        "played_at": played_at,
        "correct": record["correct"],
        "total": record["total"],
        "hints_used": record.get("hints_used", 0),
        "percentage": record["percentage"],
    }


def check_score_numbers(score: dict) -> None:
    """점수의 숫자와 범위를 확인한다."""
    correct = score.get("correct")
    total = score.get("total")
    percentage = score.get("percentage")
    hints = score.get("hints_used", 0)

    if any(type(number) is not int for number in (correct, total, percentage, hints)):
        raise ValueError("점수 값은 정수여야 합니다.")
    if total <= 0 or not 0 <= correct <= total:
        raise ValueError("정답 수 또는 전체 문제 수가 올바르지 않습니다.")
    if not 0 <= percentage <= 100 or not 0 <= hints <= total:
        raise ValueError("점수 또는 힌트 횟수가 올바르지 않습니다.")


def backup_broken_file(path: Path, output: OutputFunction) -> Optional[Path]:
    """손상 파일을 백업하고 최근 세 개만 남긴다."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = path.with_name(f"{path.name}.broken-{timestamp}.bak")

    try:
        shutil.copy2(path, backup)
        backups = sorted(path.parent.glob(f"{path.name}.broken-*.bak"), reverse=True)
        for old_backup in backups[BACKUP_LIMIT:]:
            old_backup.unlink()
        return backup
    except OSError as error:
        output(f"상태 파일 백업 또는 정리에 실패했습니다: {error}")
        return None
