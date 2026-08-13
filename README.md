# AI 탐험 퀴즈 게임

Python을 처음 배우는 사람이 변수, 조건문, 반복문, 함수, 클래스, JSON 파일,
예외 처리와 Git을 한 프로젝트에서 연습할 수 있도록 만든 터미널 게임입니다.

- 기본 퀴즈: AI와 Python 기초 18개
- 실행 환경: Python 3.10 이상
- 외부 라이브러리: 없음
- GitHub: [vivleon/ia-codyssey-2](https://github.com/vivleon/ia-codyssey-2)
- 자동 테스트: 34개

## 1. 먼저 실행해 보기

```bash
git clone https://github.com/vivleon/ia-codyssey-2.git
cd ia-codyssey-2
python3 main.py
```

실행하면 다음 메뉴가 나옵니다.

```text
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 퀴즈 삭제
6. 종료
```

퀴즈 풀기에서는 먼저 풀 문제 수를 선택합니다. 문제는 무작위로 출제되며,
정답 입력 중 `h`를 입력하면 힌트를 볼 수 있습니다. 힌트 한 번당 최종
점수에서 10점이 차감됩니다.

## 2. 프로그램이 제공하는 기능

| 기능 | 설명 |
| --- | --- |
| 퀴즈 풀기 | 문제 수 선택, 무작위 출제, 정답·오답 판정 |
| 힌트 | 문제마다 한 번 사용 가능, 한 번당 10점 감점 |
| 퀴즈 추가 | 문제, 선택지 4개, 정답 번호, 힌트 입력 |
| 퀴즈 목록 | 문제, 선택지, 정답, 힌트 확인 |
| 퀴즈 삭제 | 번호로 삭제하고 즉시 파일에 저장 |
| 점수 확인 | 최고 점수와 모든 게임 기록 확인 |
| 자동 저장 | 퀴즈, 점수, 날짜·시간을 `state.json`에 저장 |
| 안전 종료 | 정상 종료, `Ctrl+C`, EOF에서 상태 저장 시도 |
| 손상 복구 | 손상 파일을 백업하고 기본 퀴즈 18개로 복구 |

잘못된 입력은 프로그램을 끝내지 않고 다시 받습니다.

| 입력 | 처리 |
| --- | --- |
| 빈 입력 | `값을 입력해 주세요.` 또는 `내용을 입력해 주세요.` |
| 숫자 대신 문자 | `숫자로 입력해 주세요.` |
| 범위 밖 숫자 | 현재 입력 가능한 범위를 안내 |
| 중복 선택지 | 다른 선택지를 다시 입력하도록 안내 |
| `Ctrl+C` 또는 EOF | 안전 종료 안내 후 저장 |

## 3. 코드는 이 순서로 읽으세요

처음부터 모든 파일을 이해할 필요는 없습니다.

```text
main.py
  ↓
quiz.py
  ↓
quiz_game.py
  ↓
storage.py
```

| 순서 | 파일 | 처음 볼 내용 |
| ---: | --- | --- |
| 1 | `main.py` | 프로그램이 어디에서 시작하는가? |
| 2 | `quiz.py` | 퀴즈 한 개는 어떤 데이터와 동작을 가지는가? |
| 3 | `quiz_game.py` | 메뉴와 게임은 어떤 순서로 진행되는가? |
| 4 | `storage.py` | JSON을 어떻게 안전하게 읽고 쓰는가? |
| 5 | `defaults.py` | 기본 퀴즈 18개는 어떻게 만들어지는가? |
| 6 | `tests/` | 각 기능이 실제로 동작하는지 어떻게 확인하는가? |

`storage.py`는 백업과 데이터 검증이 있어 가장 어렵습니다. 먼저
`main.py`, `quiz.py`, `quiz_game.py`만 읽고 게임 흐름을 이해한 다음 보세요.

각 Python 파일에는 초보자용 설명 주석을 넣었습니다. 함수 위의 큰따옴표 세 개
(`"""..."""`)는 함수의 목적과 원리를 설명하는 **docstring**이고, `#` 주석은
해당 코드에서 헷갈리기 쉬운 이유를 설명합니다. 먼저 docstring으로 전체 목적을
파악한 뒤 함수 안의 `#` 주석과 코드를 함께 읽으면 됩니다.

## 4. Python 기초를 코드로 이해하기

### 4.1 변수

변수는 값을 기억하기 위해 붙이는 이름입니다.

```python
correct_count = 0
hints_used = 0
```

정답을 맞히면 `correct_count`를 1 증가시킵니다. 이름이 있기 때문에 숫자 `0`이
무엇을 뜻하는지 알 수 있습니다.

### 4.2 기본 자료형

| 자료형 | 뜻 | 프로젝트 예시 |
| --- | --- | --- |
| `int` | 정수 | 정답 번호, 점수, 문제 수 |
| `str` | 문자열 | 문제, 선택지, 힌트 |
| `bool` | 참 또는 거짓 | 정답 여부, 힌트 사용 여부 |
| `list` | 순서가 있는 여러 값 | 퀴즈 목록, 선택지 목록 |
| `dict` | 이름과 값을 묶은 데이터 | 최고 점수, 게임 기록 |

### 4.3 조건문 `if/elif/else`

조건에 따라 다른 코드를 실행합니다. 메뉴 번호에 따라 기능을 선택하는 부분이
가장 쉬운 예입니다.

```python
if menu == 1:
    self.play_quiz()
elif menu == 2:
    self.add_quiz()
else:
    self.running = False
```

### 4.4 반복문 `for`와 `while`

- `for`: 개수가 정해진 목록을 하나씩 볼 때 사용합니다.
- `while`: 특정 조건이 끝날 때까지 계속 반복할 때 사용합니다.

```python
for quiz in questions:
    # 문제를 하나씩 출제

while self.running:
    # 종료를 선택할 때까지 메뉴 반복
```

### 4.5 함수, 매개변수, 반환값

함수는 여러 코드를 하나의 이름으로 묶은 것입니다.

```python
def _make_result(self, correct, total, hints):
    # correct, total, hints는 매개변수
    return result  # 계산 결과를 반환
```

이 프로젝트는 긴 작업을 짧은 함수로 나눴습니다.

```text
play_quiz()
├─ _choose_questions()      문제 섞기와 문제 수 선택
├─ _solve_one_question()    문제 한 개 출제와 판정
├─ _make_result()           점수 계산
└─ _finish_game()           결과 출력과 저장
```

## 5. 클래스와 객체

### 5.1 클래스란?

클래스는 데이터와 관련 동작을 함께 정의한 설계도입니다. 클래스로 실제 만든
값을 객체라고 합니다.

```python
quiz = Quiz("문제", ["1", "2", "3", "4"], 1, "힌트")
```

여기서 `Quiz`는 클래스이고 `quiz`는 객체입니다.

### 5.2 `Quiz` 클래스

`Quiz`는 문제 한 개만 담당합니다.

| 종류 | 이름 | 역할 |
| --- | --- | --- |
| 속성 | `question` | 문제 문장 |
| 속성 | `choices` | 선택지 4개 |
| 속성 | `answer` | 정답 번호 |
| 속성 | `hint` | 힌트 |
| 메서드 | `is_correct()` | 선택한 번호가 정답인지 확인 |
| 메서드 | `to_dict()` | JSON 저장용 사전으로 변환 |
| 메서드 | `from_dict()` | 사전에서 Quiz 객체 생성 |

### 5.3 `QuizGame` 클래스

`QuizGame`은 여러 퀴즈와 게임 전체를 담당합니다.

| 영역 | 메서드 | 역할 |
| --- | --- | --- |
| 메뉴 | `run()` | 메뉴 반복과 안전 종료 |
| 입력 | `_read_int()`, `_read_text()` | 숫자·문자열 검증 |
| 플레이 | `play_quiz()` | 퀴즈 진행 전체 순서 |
| 관리 | `add_quiz()`, `list_quizzes()`, `delete_quiz()` | 퀴즈 관리 |
| 점수 | `_make_result()`, `_is_new_best()` | 점수 계산과 비교 |
| 저장 연결 | `load_state()`, `save_state()` | `storage.py` 호출 |

### 5.4 `__init__`과 `self`

`__init__`은 객체가 만들어질 때 처음 실행되는 메서드입니다. `self`는 지금
사용 중인 객체 자신을 뜻합니다.

```python
self.quizzes = []
self.best_score = None
self.score_history = []
```

이 값들은 같은 `QuizGame` 객체의 여러 메서드에서 함께 사용됩니다.

### 5.5 왜 함수만 사용하지 않았나?

퀴즈 목록, 최고 점수, 파일 경로는 메뉴·플레이·저장 기능이 함께 사용합니다.
함수만 사용하면 이 값을 계속 매개변수로 전달해야 합니다. 클래스에 저장하면
`self.quizzes`처럼 같은 상태를 쉽게 공유할 수 있습니다. 반대로 상태가 없는
JSON 보조 작업은 `storage.py`의 함수로 분리했습니다.

## 6. 프로그램 실행 흐름

```text
main.py의 main()
└─ QuizGame 객체 생성
   └─ load_state()로 state.json 읽기
      └─ run()으로 메뉴 시작
         ├─ 1: play_quiz()
         ├─ 2: add_quiz()
         ├─ 3: list_quizzes()
         ├─ 4: show_best_score()
         ├─ 5: delete_quiz()
         └─ 6: 종료 후 save_state()
```

`Ctrl+C`나 EOF가 발생해도 `run()`의 `finally`에서 `save_state()`를
호출합니다. `finally`는 오류 발생 여부와 관계없이 마지막에 실행되는
구역입니다.

## 7. 파일 입출력과 JSON

### 7.1 파일 읽기와 쓰기

파일은 다음 순서로 다룹니다.

```python
with path.open("r", encoding="utf-8") as file:
    data = json.load(file)
```

1. `open()`으로 파일을 엽니다.
2. `json.load()`로 JSON을 Python 값으로 읽습니다.
3. `with` 블록이 끝나면 파일이 자동으로 닫힙니다.

### 7.2 JSON을 사용하는 이유

JSON은 사람이 읽을 수 있는 가벼운 텍스트 형식입니다. Python의 `dict`,
`list`, `str`, `int`와 자연스럽게 대응하며 별도 데이터베이스가 필요 없습니다.
작은 학습 프로젝트에는 적합하지만, 대규모 검색·부분 수정·동시 쓰기에는
SQLite 같은 데이터베이스가 더 적합합니다.

### 7.3 저장 구조

```json
{
  "schema_version": 2,
  "quizzes": [
    {
      "question": "문제",
      "choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
      "answer": 1,
      "hint": "힌트"
    }
  ],
  "best_score": {
    "correct": 4,
    "total": 5,
    "percentage": 70,
    "hints_used": 1
  },
  "score_history": [
    {
      "played_at": "2026-08-13T10:00:00+09:00",
      "correct": 4,
      "total": 5,
      "hints_used": 1,
      "percentage": 70
    }
  ]
}
```

이전 v1 파일에는 `hint`, `score_history`, `schema_version`이 없을 수 있습니다.
프로그램은 누락된 값에 기본값을 사용하므로 이전 파일도 읽을 수 있습니다.

### 7.4 `try/except`가 필요한 이유

파일이 없거나, JSON이 깨졌거나, 쓰기 권한 또는 디스크 공간이 부족할 수
있습니다. `try`에는 실패할 수 있는 코드를, `except`에는 실패했을 때 할 일을
작성합니다.

손상된 파일은 다음 순서로 처리합니다.

1. 원본을 `state.json.broken-날짜.bak`으로 복사합니다.
2. 최근 백업 3개만 남깁니다.
3. 기본 퀴즈 18개로 정상 JSON을 다시 만듭니다.

저장할 때는 `.state.json.tmp`를 먼저 완성한 뒤 `state.json`으로 교체합니다.
이 방식은 저장 중 프로그램이 중단돼 원본이 절반만 기록될 위험을 줄입니다.

## 8. 보너스 과제 충족

| 보너스 | 구현 방법 | 테스트 |
| --- | --- | --- |
| 랜덤 출제 | 복사한 목록에 `random.shuffle()` 사용 | `test_questions_are_shuffled_before_selection` |
| 문제 수 선택 | 1~전체 문제 수를 입력받아 목록 자르기 | `test_player_selects_question_count` |
| 힌트 | `Quiz.hint`, `h` 입력, 문제당 1회 | `test_hint_is_shown_once_and_deducts_ten_points` |
| 힌트 감점 | `힌트 수 × 10점`, 최저 0점 | 같은 테스트에서 90점 확인 |
| 퀴즈 삭제 | 삭제 후 저장, 실패하면 목록 복구 | `test_delete_quiz_rolls_back_when_save_fails` |
| 점수 히스토리 | 날짜·문제 수·정답·힌트·점수 저장 | `test_every_completed_game_is_saved_to_history` |

## 9. 테스트

```bash
python3 -m unittest discover -v
```

2026-08-13 기준 34개 테스트가 통과합니다.

| 테스트 파일 | 확인 내용 |
| --- | --- |
| `tests/test_quiz.py` | Quiz 검증, 정답 판정, JSON 변환 |
| `tests/test_menu.py` | 메뉴, 입력 범위, EOF 종료 |
| `tests/test_play.py` | 랜덤 출제, 문제 수, 힌트, 점수, 기록 |
| `tests/test_game_features.py` | 저장, 복구, 추가, 삭제, v1 호환 |

## 10. Git 기초와 수행 증빙

### 10.1 Git이 필요한 이유

Git은 파일의 변경 이력을 기록합니다. 언제 무엇을 바꿨는지 확인하고, 문제가
생기면 이전 상태를 찾고, 여러 사람이 각자 작업한 내용을 합칠 수 있습니다.

| 명령 | 뜻 |
| --- | --- |
| `git init` | 현재 폴더에 새 Git 저장소 만들기 |
| `git add` | 다음 커밋에 포함할 변경 선택 |
| `git commit` | 선택한 변경을 이력으로 기록 |
| `git push` | 로컬 커밋을 GitHub로 전송 |
| `git pull` | GitHub의 새 변경을 가져와 통합 |
| `git checkout` | 브랜치 만들기 또는 이동 |
| `git clone` | 원격 저장소 전체를 새 폴더에 복제 |

### 10.2 커밋과 원격 저장소

이번 초보자용 코드 주석 보강 커밋을 게시하면 `main`에는 의미 있는 커밋 26개가
있습니다.

```bash
git remote get-url origin
git rev-list --count origin/main
git log --oneline --graph --decorate --all
```

- 원격: `https://github.com/vivleon/ia-codyssey-2.git`
- 기능 브랜치: `codex/quiz-play`
- 비빠른 병합 커밋: `9a0d68d`
- clone/pull 실습 커밋: `272f5fe`
- 상세 기록: [`docs/git-evidence.txt`](docs/git-evidence.txt)

브랜치는 안정적인 `main`과 새 기능 작업을 분리합니다. merge는 검증된 브랜치의
변경을 `main`에 합치는 작업입니다. `--no-ff`를 사용하면 분기와 병합 기록이
그래프에 남습니다.

커밋 메시지는 한 커밋에 한 목적을 담아 다음 형식을 사용합니다.

```text
Type(Scope): 변경 요약
```

예: `Refactor(beginner): 퀴즈 게임 흐름 단순화`

## 11. 데이터가 1,000개 이상이면?

현재 JSON 방식은 실행할 때 전체 파일을 읽고 저장할 때 전체 파일을 다시
씁니다. 검색도 앞에서부터 하나씩 확인하므로 O(N)입니다.

| 한계 | 개선 방법 |
| --- | --- |
| 전체 파일 읽기·쓰기 | SQLite에서 필요한 행만 읽고 수정 |
| 순차 검색 O(N) | 고유 ID와 검색 인덱스 사용 |
| 전체 목록 메모리 적재 | 페이지 단위로 조회 |
| 동시 저장 충돌 | 데이터베이스 트랜잭션 사용 |

2026-08-13 측정에서 1,000개 JSON은 약 255.9KiB, 저장 중앙값 6.66ms,
로드 중앙값 9.42ms였습니다. 자세한 재현 방법은
[`docs/state-benchmark.md`](docs/state-benchmark.md)에 있습니다.

## 12. 요구사항이 바뀌면 어디를 수정할까?

| 변경 내용 | 먼저 볼 파일·함수 | 테스트 |
| --- | --- | --- |
| 정답 판정 | `quiz.py: is_correct()` | `tests/test_quiz.py` |
| 선택지 수 | `Quiz.__post_init__()`, 입력·출제 범위 | 모델·플레이 테스트 |
| 점수 계산 | `_make_result()`, `_is_new_best()` | `tests/test_play.py` |
| 힌트 감점 | `HINT_PENALTY`, `_read_answer()` | 힌트 테스트 |
| 메뉴 기능 | `MENU`, `run()` | `tests/test_menu.py` |
| 저장 구조 | `storage.py`, `Quiz.to_dict()/from_dict()` | 영속성·복구 테스트 |

변경 전후에 전체 테스트를 실행해 기존 기능과 이전 JSON 파일의 호환성을
확인합니다.

## 13. 동료평가 예상 질문과 짧은 답변

| 질문 | 바로 말할 답변 |
| --- | --- |
| 메뉴 기능이 모두 동작하나요? | 1~6번을 `run()`의 `if/elif`로 연결했고 34개 테스트로 확인했습니다. |
| 입력 오류는 어떻게 처리하나요? | `_read_int()`와 `_read_text()`가 올바른 값이 들어올 때까지 다시 묻습니다. |
| 재실행해도 데이터가 남나요? | 변경 직후와 종료 시 JSON에 저장하고 생성자에서 다시 읽습니다. |
| 기본 문제는 몇 개인가요? | 힌트를 포함한 AI·Python 기초 문제 18개입니다. |
| 클래스 책임은 어떻게 나눴나요? | `Quiz`는 문제 하나, `QuizGame`은 게임 전체, `storage.py`는 파일을 담당합니다. |
| 왜 클래스를 사용했나요? | 퀴즈 목록과 점수처럼 여러 기능이 공유하는 상태를 객체에 보관하기 위해서입니다. |
| JSON을 선택한 이유는? | 사람이 읽기 쉽고 Python 기본 자료형과 잘 맞으며 별도 설치가 필요 없기 때문입니다. |
| `try/except`가 필요한 이유는? | 파일 손상·권한·JSON 문법 오류에도 프로그램이 안내하고 복구하도록 하기 위해서입니다. |
| 안전 종료는 어떻게 하나요? | `Ctrl+C`와 EOF를 처리하고 `finally`에서 저장합니다. |
| 랜덤 출제는 어떻게 하나요? | 원본 목록을 복사한 뒤 `random.shuffle()`로 섞습니다. |
| 힌트 점수는? | 문제당 한 번, 사용 횟수마다 최종 점수에서 10점을 뺍니다. |
| 삭제 저장에 실패하면? | 삭제한 객체를 원래 위치에 다시 넣어 삭제를 취소합니다. |
| 모든 점수도 저장하나요? | 날짜·시간, 문제 수, 정답 수, 힌트 수, 최종 점수를 매 게임 저장합니다. |
| 브랜치를 왜 사용했나요? | 안정적인 `main`과 기능 개발을 분리하고 검증 후 병합하기 위해서입니다. |
| 1,000개 이상이면? | 전체 파일 처리와 O(N) 검색이 한계라서 인덱스와 SQLite를 검토합니다. |
| 채점 방식이 바뀌면? | `_make_result()`와 관련 테스트부터 수정합니다. |

## 14. 제출 증빙

| 증빙 | 파일 |
| --- | --- |
| 개발 환경과 초기 테스트 | [`01-development-environment.png`](docs/screenshots/01-development-environment.png) |
| 퀴즈 추가 | [`02-add-quiz.png`](docs/screenshots/02-add-quiz.png) |
| 퀴즈 목록 | [`03-quiz-list.png`](docs/screenshots/03-quiz-list.png) |
| 퀴즈 플레이와 점수 | [`04-play-and-score.png`](docs/screenshots/04-play-and-score.png) |
| Git 브랜치와 병합 그래프 | [`05-git-log-graph.png`](docs/screenshots/05-git-log-graph.png) |

평가 직전에는 다음 명령과 실제 게임 실행을 함께 확인합니다.

```bash
python3 -m unittest discover -v
python3 main.py
git rev-list --count origin/main
git log --oneline --graph --decorate --all
```
