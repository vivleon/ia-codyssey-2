"""state.json을 저장하고 불러오는 파일"""

import json
import os
import shutil

from defaults import get_default_quizzes
from quiz import Quiz


def make_new_state():
    """처음 실행할 때 사용할 기본 데이터를 만든다."""
    quizzes = get_default_quizzes()
    best_score = None
    score_history = []

    return quizzes, best_score, score_history


def load_state(filename):
    """state.json을 읽어서 게임 데이터를 돌려준다."""
    # 파일이 없으면 첫 실행이므로 기본 데이터를 사용한다.
    if not os.path.exists(filename):
        return make_new_state()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # JSON 안의 dict를 Quiz 객체로 하나씩 바꾼다.
        quizzes = []

        for quiz_data in data["quizzes"]:
            quizzes.append(Quiz.from_dict(quiz_data))

        best_score = data.get("best_score")
        score_history = data.get("score_history", [])

        # JSON 문법은 맞아도 내용이 틀릴 수 있으므로 확인한다.
        if best_score is not None and not isinstance(best_score, dict):
            raise ValueError("최고 점수 데이터가 올바르지 않습니다.")

        if not isinstance(score_history, list):
            raise ValueError("점수 기록 데이터가 올바르지 않습니다.")

        print("저장된 데이터를 불러왔습니다.")
        return quizzes, best_score, score_history

    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        print("상태 파일이 손상되어 기본 데이터로 복구합니다.")

        # 손상된 파일은 state.json.bak으로 한 번 보관한다.
        try:
            shutil.copyfile(filename, filename + ".bak")
        except OSError:
            print("손상된 파일을 백업하지 못했습니다.")

        quizzes, best_score, score_history = make_new_state()
        save_state(filename, quizzes, best_score, score_history)

        return quizzes, best_score, score_history


def save_state(filename, quizzes, best_score, score_history):
    """현재 게임 데이터를 UTF-8 JSON 파일로 저장한다."""
    quiz_list = []

    for quiz in quizzes:
        quiz_list.append(quiz.to_dict())

    data = {
        "quizzes": quiz_list,
        "best_score": best_score,
        "score_history": score_history,
    }

    # 임시 파일을 먼저 완성한 뒤 원래 파일로 바꾼다.
    # 저장 도중 문제가 생겨 기존 파일이 깨지는 일을 줄이는 방법이다.
    temp_file = filename + ".tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        os.replace(temp_file, filename)
        return True

    except OSError:
        print("상태 파일을 저장하지 못했습니다.")
        return False
