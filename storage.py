"""state.json 읽기, 검증, 저장, 손상 복구를 담당하는 파일.

게임 흐름을 처음 공부할 때는 이 파일을 나중에 읽어도 됩니다.
``quiz_game.py``가 사용자 기능을 담당하고 이 파일은 파일 처리만 담당한다.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from defaults import build_default_quizzes
from quiz import Quiz


# 저장 형식이 바뀌면 버전 숫자로 어떤 구조인지 구분할 수 있다.
SCHEMA_VERSION = 2
# 손상 백업이 무한히 늘지 않도록 최신 파일 세 개만 보관한다.
BACKUP_LIMIT = 3
# 긴 타입을 짧은 이름으로 표현해 함수의 입력과 반환 구조를 읽기 쉽게 한다.
OutputFunction = Callable[[str], None]
GameState = Tuple[List[Quiz], Optional[dict], List[dict]]


def load_state_file(path: Path, output: OutputFunction) -> GameState:
    """JSON을 읽어 ``(퀴즈, 최고 점수, 게임 기록)``으로 반환한다.

    파일 없음은 첫 실행이므로 정상 상황으로 보고 기본값을 사용한다. 파일 읽기,
    JSON 해석, 데이터 검증 중 문제가 생기면 손상 파일을 보관한 뒤 기본값으로
    복구한다. 이렇게 하면 사용자에게 오류만 보여 주고 종료하는 일을 막을 수 있다.
    """
    if not path.exists():
        return default_state()

    try:
        # with 블록을 벗어나면 성공·실패와 관계없이 파일이 자동으로 닫힌다.
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        # JSON 문법이 맞아도 필드가 잘못될 수 있으므로 구조 검증을 따로 한다.
        return parse_state(data)

    # 예상 가능한 파일·JSON·검증 오류만 잡고, 프로그래밍 오류는 숨기지 않는다.
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        output(f"상태 파일을 읽을 수 없어 기본 데이터로 복구합니다: {error}")
        backup = backup_broken_file(path, output)
        if backup:
            output(f"기존 상태 파일 백업: {backup}")

        quizzes, best_score, history = default_state()
        save_state_file(path, quizzes, best_score, history, output)
        return quizzes, best_score, history


def default_state() -> GameState:
    """첫 실행 또는 복구에 사용할 기본 퀴즈 18개와 빈 기록을 만든다."""
    return build_default_quizzes(), None, []


def parse_state(data: object) -> GameState:
    """JSON의 최상위 구조와 각 하위 항목을 검증해 GameState로 바꾼다.

    ``json.load``는 문법만 확인해 dict/list 같은 Python 값으로 바꾼다. 프로그램이
    기대하는 필드명, 자료형, 숫자 범위까지 안전하다는 뜻은 아니므로 이 단계에서
    순서대로 검증한다.
    """
    if not isinstance(data, dict):
        raise ValueError("최상위 데이터는 객체여야 합니다.")

    # 버전 필드가 없던 예전 파일은 버전 1로 간주해 계속 읽을 수 있게 한다.
    version = data.get("schema_version", 1)
    quizzes = data.get("quizzes")
    history = data.get("score_history", [])

    # type(...) is int는 bool을 정수 버전으로 잘못 허용하지 않는다.
    if type(version) is not int or version not in (1, SCHEMA_VERSION):
        raise ValueError("지원하지 않는 상태 파일 버전입니다.")
    if not isinstance(quizzes, list):
        raise ValueError("quizzes는 목록이어야 합니다.")
    if not isinstance(history, list):
        raise ValueError("score_history는 목록이어야 합니다.")

    # 각 항목의 세부 검증은 해당 데이터를 가장 잘 아는 함수에 맡긴다.
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
    """현재 상태를 임시 파일에 완전히 쓴 뒤 state.json으로 교체한다.

    기존 파일에 바로 쓰다가 전원 종료나 디스크 오류가 나면 JSON이 절반만 남을
    수 있다. 같은 폴더의 임시 파일을 먼저 완성하고 ``replace``하면 교체 순간
    전까지 기존 파일이 유지된다. 이를 원자적 저장(atomic save) 방식이라고 한다.
    성공하면 True, 파일 작업에 실패하면 False를 반환한다.
    """
    # 객체인 Quiz는 to_dict()로 JSON 기본 자료형으로 변환한다.
    data = {
        "schema_version": SCHEMA_VERSION,
        "quizzes": [quiz.to_dict() for quiz in quizzes],
        "best_score": best_score,
        "score_history": history,
    }
    # 같은 파일 시스템 안에서 replace가 안전하게 작동하도록 같은 폴더를 쓴다.
    temporary_file = path.with_name(f".{path.name}.tmp")

    try:
        # 저장 폴더가 없으면 상위 폴더까지 만들고, 이미 있어도 오류를 내지 않는다.
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_file.open("w", encoding="utf-8") as file:
            # ensure_ascii=False는 한글을 \uXXXX가 아닌 읽을 수 있는 글자로 보존한다.
            # indent=2는 들여쓰기를 넣어 사람이 state.json을 확인하기 쉽게 한다.
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        # 임시 파일 쓰기가 끝난 뒤에만 실제 state.json을 한 번에 교체한다.
        temporary_file.replace(path)
        return True
    except OSError as error:
        output(f"상태 파일을 저장하지 못했습니다: {error}")
        output(f"저장 대상: {path}")
        output(f"임시 파일이 남아 있다면 확인하세요: {temporary_file}")
        return False


def validate_best_score(score: object) -> Optional[dict]:
    """최고 점수의 자료형·범위를 검사해 안전한 새 dict로 반환한다.

    이전 저장 형식에는 ``hints_used``가 없을 수 있으므로 필수값으로 강제하지
    않는다. 이것이 오래된 데이터도 계속 읽을 수 있게 하는 하위 호환 처리다.
    """
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
    """게임 기록의 점수와 날짜 형식을 확인하고 필요한 필드만 반환한다."""
    if not isinstance(record, dict):
        raise ValueError("게임 기록은 객체여야 합니다.")

    check_score_numbers(record)
    played_at = record.get("played_at")
    if not isinstance(played_at, str):
        raise ValueError("게임 기록 시간은 문자열이어야 합니다.")

    # 문자열이라는 사실만으로 날짜가 유효한 것은 아니므로 실제로 변환해 본다.
    try:
        parsed_time = datetime.fromisoformat(played_at)
    except ValueError as error:
        raise ValueError("게임 기록 시간이 올바르지 않습니다.") from error
    # 서로 다른 지역에서 실행해도 시각을 해석할 수 있도록 시간대를 요구한다.
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
    """점수 관련 네 값이 정수이고 논리적인 범위 안인지 검사한다.

    반환값은 없고 규칙을 어기면 ValueError를 발생시킨다. 검증을 통과했다는
    사실 자체가 결과이므로 이런 함수를 validation 함수라고 부른다.
    """
    correct = score.get("correct")
    total = score.get("total")
    percentage = score.get("percentage")
    hints = score.get("hints_used", 0)

    # any는 네 값 중 조건을 만족하는 값이 하나라도 있으면 True를 반환한다.
    # type을 직접 비교해 True/False가 1/0으로 통과하지 못하게 한다.
    if any(type(number) is not int for number in (correct, total, percentage, hints)):
        raise ValueError("점수 값은 정수여야 합니다.")
    if total <= 0 or not 0 <= correct <= total:
        raise ValueError("정답 수 또는 전체 문제 수가 올바르지 않습니다.")
    if not 0 <= percentage <= 100 or not 0 <= hints <= total:
        raise ValueError("점수 또는 힌트 횟수가 올바르지 않습니다.")


def backup_broken_file(path: Path, output: OutputFunction) -> Optional[Path]:
    """손상 파일을 시간표가 붙은 이름으로 복사하고 최신 세 개만 남긴다.

    기본값으로 복구하기 전에 원본을 보존해 사용자가 수동으로 데이터를 살펴볼
    기회를 남긴다. 함수가 성공하면 백업 경로, 실패하면 None을 반환한다.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = path.with_name(f"{path.name}.broken-{timestamp}.bak")

    try:
        # copy2는 파일 내용과 함께 수정 시각 같은 메타데이터도 가능한 만큼 보존한다.
        shutil.copy2(path, backup)
        # 파일 이름에 고정 길이 시간이 들어가므로 역순 정렬하면 최신 파일이 먼저다.
        backups = sorted(path.parent.glob(f"{path.name}.broken-*.bak"), reverse=True)
        for old_backup in backups[BACKUP_LIMIT:]:
            old_backup.unlink()
        return backup
    except OSError as error:
        output(f"상태 파일 백업 또는 정리에 실패했습니다: {error}")
        return None
