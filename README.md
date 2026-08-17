# AI와 Python 기초 퀴즈

Python을 처음 배우는 사람이 만든 것처럼 기본 문법으로 작성한 터미널
퀴즈 게임입니다. 짧은 함수, `if/elif/else`, `for`, `while`, `list`, `dict`를
직접 확인할 수 있습니다.

- Python 3.10 이상
- 외부 라이브러리 없음
- 기본 문제 18개
- 클래스 2개: `Quiz`, `QuizGame`
- 자동 테스트 13개
- GitHub: [vivleon/ia-codyssey-2](https://github.com/vivleon/ia-codyssey-2)

## 1. 퀴즈 주제와 선정 이유

주제는 **AI, Python, 파일 입출력, Git 기초**입니다. 이 게임을 만드는 데 필요한
개념을 문제로 다시 풀어 볼 수 있고, 동료평가에서 코드의 원리를 설명하는 데에도
도움이 되기 때문에 선택했습니다.

## 2. 실행 방법

```bash
git clone https://github.com/vivleon/ia-codyssey-2.git
cd ia-codyssey-2
python3 main.py
```

테스트 실행 방법은 다음과 같습니다.

```bash
python3 -m unittest discover -v
```

## 3. 메뉴와 기능

```text
========================================
       AI와 Python 기초 퀴즈
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 퀴즈 삭제
6. 종료
========================================
```

| 기능 | 설명 |
| --- | --- |
| 퀴즈 풀기 | 문제 수를 고르고 무작위 순서로 풉니다. |
| 퀴즈 추가 | 문제, 선택지 4개, 정답, 힌트를 입력합니다. |
| 퀴즈 목록 | 등록된 문제를 번호와 함께 보여 줍니다. |
| 점수 확인 | 최고 점수와 모든 게임 기록을 보여 줍니다. |
| 퀴즈 삭제 | 번호를 골라 삭제하고 바로 저장합니다. |
| 종료 | 현재 상태를 저장하고 안전하게 끝냅니다. |

잘못된 입력은 프로그램을 끝내지 않고 다시 받습니다.

| 입력 | 안내 |
| --- | --- |
| 빈 입력 | 값을 입력하라는 문구 출력 |
| `abc` 같은 문자 | 숫자로 입력하라는 문구 출력 |
| 범위 밖 숫자 | 허용되는 숫자 범위 출력 |
| `Ctrl+C` 또는 EOF | 안내 후 저장하고 안전 종료 |

## 4. 보너스 과제 5종

모든 보너스 과제를 구현했습니다.

1. **랜덤 출제**: `random.shuffle()`로 문제 순서를 섞습니다.
2. **문제 수 선택**: 전체 문제 중 몇 문제를 풀지 고릅니다.
3. **힌트**: 답을 입력할 때 `h`를 누르면 힌트를 봅니다. 한 문제당 10점이
   차감됩니다.
4. **퀴즈 삭제**: 문제 번호로 삭제하고 `state.json`에 반영합니다.
5. **점수 히스토리**: 날짜·시간, 문제 수, 정답 수, 힌트 수, 점수를 매번
   저장합니다.

## 5. 파일 구조

```text
ia-codyssey-2/
├── main.py                 # 프로그램 시작
├── quiz.py                 # Quiz 클래스
├── quiz_game.py            # QuizGame 클래스와 메뉴
├── defaults.py             # 기본 퀴즈 18개
├── storage.py              # JSON 저장과 불러오기
├── state.json              # 퀴즈와 점수 데이터
├── tests/
│   ├── test_quiz.py        # Quiz 테스트
│   ├── test_game.py        # 메뉴와 보너스 테스트
│   └── test_storage.py     # 저장과 복구 테스트
├── docs/                   # Git과 실행 화면 증빙
├── .gitignore
└── README.md
```

처음 읽을 때는 다음 순서가 쉽습니다.

```text
main.py → quiz.py → quiz_game.py → storage.py → defaults.py
```

## 6. 두 클래스의 역할

### `Quiz`

퀴즈 한 문제를 담당합니다.

- 속성: `question`, `choices`, `answer`, `hint`
- `show()`: 문제와 선택지 출력
- `is_correct()`: 정답 확인
- `to_dict()`: 객체를 저장용 dict로 변경
- `from_dict()`: dict를 객체로 변경

### `QuizGame`

게임 전체를 담당합니다.

- 속성: `quizzes`, `best_score`, `score_history`, `running`
- 입력: `read_number()`, `read_text()`, `read_answer()`
- 게임: `play_quiz()`, `finish_quiz()`
- 관리: `add_quiz()`, `list_quizzes()`, `delete_quiz()`
- 저장: `save()`

`Quiz`는 한 문제만 알고, `QuizGame`은 여러 문제와 메뉴를 관리합니다. 함수만
사용하면 문제 데이터와 게임 상태를 계속 매개변수로 전달해야 하지만, 클래스는
관련 데이터와 기능을 한 객체에 묶을 수 있습니다.

## 7. 프로그램 흐름

```text
main.py
  ↓ QuizGame 객체 만들기
__init__()
  ↓ state.json 불러오기
run()
  ↓ 메뉴 반복
선택한 기능 실행
  ↓
저장 후 종료
```

퀴즈 한 게임의 흐름은 다음과 같습니다.

```text
문제 복사 → random.shuffle → 문제 수 선택 → for로 출제
→ 정답·힌트 확인 → 점수 계산 → 최고점수 비교 → 히스토리 저장
```

## 8. `state.json` 설명

`state.json`은 프로젝트 루트에 생성되는 UTF-8 JSON 파일입니다. 프로그램을
종료해도 추가한 퀴즈와 점수가 남아 있게 해 줍니다.

```json
{
  "quizzes": [
    {
      "question": "Python에서 목록을 나타내는 자료형은?",
      "choices": ["int", "str", "list", "bool"],
      "answer": 3,
      "hint": "대괄호를 사용하는 자료형입니다."
    }
  ],
  "best_score": {
    "correct": 1,
    "total": 1,
    "percentage": 100,
    "hints_used": 0
  },
  "score_history": [
    {
      "played_at": "2026-08-14T10:00:00+09:00",
      "correct": 1,
      "total": 1,
      "percentage": 100,
      "hints_used": 0
    }
  ]
}
```

| 필드 | 뜻 |
| --- | --- |
| `quizzes` | 모든 퀴즈의 목록 |
| `best_score` | 지금까지 가장 좋은 결과, 미응시는 `null` |
| `score_history` | 날짜와 시간을 포함한 모든 게임 결과 |

### 읽기와 쓰기

- 읽기: `open()` → `json.load()` → `Quiz.from_dict()`
- 쓰기: `Quiz.to_dict()` → 임시 파일 → `json.dump()` → `os.replace()`
- 한글: `encoding="utf-8"`, `ensure_ascii=False`

임시 파일을 먼저 완성하고 교체하므로 쓰기 도중 기존 파일이 절반만 남을 위험을
줄입니다. 파일이 없으면 기본 문제 18개를 사용합니다. 파일이 손상되면
`state.json.bak`으로 복사한 뒤 기본 데이터로 다시 시작합니다.

JSON은 사람이 읽기 쉽고 Python의 `list`, `dict`, `str`, `int`와 잘 맞으며
별도 프로그램이 필요 없어서 선택했습니다.

## 9. Python 기초 설명

### 변수

변수는 값을 기억하기 위해 붙이는 이름입니다.

```python
correct_count = 0
hint_count = 0
```

### 기본 자료형

| 자료형 | 뜻 | 예시 |
| --- | --- | --- |
| `int` | 정수 | 문제 수, 점수 |
| `str` | 글자 | 문제, 힌트 |
| `bool` | 참 또는 거짓 | 힌트 사용 여부 |
| `list` | 순서가 있는 여러 값 | 퀴즈 목록 |
| `dict` | 이름과 값을 묶은 값 | 점수 기록 |

### 조건문

`if/elif/else`는 조건에 따라 다른 코드를 실행합니다. 메뉴 번호 선택과 정답
판정에 사용했습니다.

### 반복문

- `for`: 개수가 정해진 퀴즈나 선택지를 하나씩 볼 때 사용합니다.
- `while`: 올바른 입력을 받을 때까지 계속 반복할 때 사용합니다.

### 함수

함수는 여러 줄의 작업에 이름을 붙인 것입니다. 매개변수는 함수가 받을 값이고,
`return`은 함수가 돌려주는 값입니다.

```python
def is_correct(self, selected):
    return selected == self.answer
```

### `__init__`과 `self`

`__init__`은 객체를 만들 때 처음 실행됩니다. `self`는 현재 객체 자신을 뜻합니다.
`self.question`은 각각의 Quiz 객체가 가진 문제입니다.

### `try/except/finally`

- `try`: 오류가 생길 수 있는 코드
- `except`: 오류가 생겼을 때 실행할 코드
- `finally`: 오류 여부와 상관없이 마지막에 실행할 코드

숫자 변환, JSON 읽기·쓰기, `Ctrl+C`, EOF를 안전하게 처리하는 데 사용했습니다.

## 10. Git 작업 방법

| 명령 | 뜻 |
| --- | --- |
| `git init` | 현재 폴더를 Git 저장소로 만들기 |
| `git add` | 커밋할 변경 선택 |
| `git commit` | 변경을 하나의 기록으로 저장 |
| `git push` | 로컬 커밋을 GitHub에 보내기 |
| `git pull` | GitHub 변경을 가져와 합치기 |
| `git checkout` | 브랜치 만들기 또는 이동 |
| `git clone` | 원격 저장소를 새 폴더에 복제 |

이번 전면 재작성은 다음 브랜치에서 작업했습니다.

```bash
git checkout -b codex/simple-quiz-rebuild
git add 파일명
git commit -m "변경 내용"
git checkout main
git merge --no-ff codex/simple-quiz-rebuild
```

브랜치는 안정적인 `main`과 새 작업을 분리합니다. merge는 브랜치에서 확인한
변경을 `main`에 합치는 작업입니다. `--no-ff`를 사용하면 병합 기록이 그래프에
남습니다.

커밋은 기능별로 나누고 다음처럼 작성합니다.

```text
Feat(game): 퀴즈 출제 기능 구현
Fix(storage): 손상 파일 복구 오류 수정
Docs(readme): 실행 방법 추가
```

clone과 pull 실습 및 과거 병합 기록은
[`docs/git-evidence.txt`](docs/git-evidence.txt)에서 확인할 수 있습니다.

## 11. 평가 문항별 구현 위치와 바로 답할 내용

이 장은 동료평가 때 빠르게 찾아보기 위한 **평가용 색인**입니다. 답변을 먼저
말하고, 평가자가 근거를 요청하면 연결된 코드나 테스트를 보여 주면 됩니다.

### 11.1 항목 1 — 기능 동작 검증

| 평가 질문 | 어디에 구현했는가? | 바로 답할 내용과 확인 방법 |
| --- | --- | --- |
| 메뉴와 퀴즈 풀기·추가·목록·점수 기능이 모두 동작하는가? | [`show_menu()`와 `run()`](quiz_game.py#L25), [`play_quiz()`](quiz_game.py#L145), [`add_quiz()`](quiz_game.py#L224), [`list_quizzes()`](quiz_game.py#L256), [`show_scores()`](quiz_game.py#L286) | “`run()`의 `while`이 메뉴를 반복하고 `if/elif/else`가 번호에 맞는 메서드를 하나씩 호출합니다.” `python3 main.py`로 직접 확인합니다. |
| 정답·오답 판정과 공백·문자·범위 밖 입력을 처리하는가? | [`Quiz.is_correct()`](quiz.py#L51), [`read_number()`](quiz_game.py#L68), [`read_answer()`](quiz_game.py#L117) | “정답 번호는 `is_correct()`에서 비교합니다. 입력은 `strip()` 후 빈 값, `int()` 변환 실패, 범위 오류를 검사하고 `while`로 다시 받습니다.” [`test_wrong_number_is_asked_again`](tests/test_game.py#L22)이 확인합니다. |
| 재실행해도 추가 퀴즈와 최고 점수가 유지되는가? | [`load_state()`](storage.py#L66), [`save_state()`](storage.py#L109), [`QuizGame.__init__()`](quiz_game.py#L15) | “시작할 때 `state.json`을 읽고, 퀴즈 추가·삭제·게임 완료와 종료 때 다시 저장하므로 재실행해도 유지됩니다.” [`test_save_and_load`](tests/test_storage.py#L26)과 [`test_add_and_delete_quiz`](tests/test_game.py#L58)가 확인합니다. |
| 기본 퀴즈가 5개 이상인가? | [`get_default_quizzes()`](defaults.py#L6) | “직접 작성한 기본 퀴즈가 18개 있습니다.” [`test_missing_file_uses_defaults`](tests/test_storage.py#L19)에서 18개인지 검사합니다. |
| GitHub에 코드와 10개 이상의 의미 있는 커밋이 있는가? | [GitHub 저장소](https://github.com/vivleon/ia-codyssey-2), [`docs/git-evidence.txt`](docs/git-evidence.txt) | “기능·테스트·문서 단위로 커밋했고, 이 README 업데이트 반영 후 `main`은 35개 커밋입니다.” `git rev-list --count HEAD`로 확인합니다. |
| 브랜치 생성과 병합 기록이 그래프에 있는가? | 브랜치 `codex/simple-quiz-rebuild`, 병합 커밋 `8016b24`, [`docs/git-evidence.txt`](docs/git-evidence.txt) | “기능 브랜치에서 여섯 개 커밋으로 작업하고 `git merge --no-ff`로 `main`에 병합했습니다.” `git log --oneline --graph --decorate --all`로 확인합니다. |
| clone과 pull 실습 흔적이 있는가? | clone/pull 실습 커밋 `272f5fe`, [`docs/git-evidence.txt`](docs/git-evidence.txt) | “별도 폴더에 clone한 뒤 변경을 push하고 기존 폴더에서 pull하는 실습을 완료했습니다. 이번 병합 전에도 `git pull --ff-only origin main`으로 최신 상태를 확인했습니다.” |

### 11.2 항목 2 — 코드 구조와 설계

| 평가 질문 | 어디에 구현했는가? | 바로 답할 내용 |
| --- | --- | --- |
| `Quiz`와 `QuizGame`의 책임을 어떻게 나눴는가? | [`Quiz`](quiz.py#L4), [`QuizGame`](quiz_game.py#L11) | “`Quiz`는 문제 한 개의 데이터·출력·정답 판정을 담당하고, `QuizGame`은 여러 문제, 메뉴, 입력, 점수와 게임 전체 흐름을 담당합니다.” |
| 입력, 게임 진행, 저장을 어떤 기준으로 분리했는가? | 입력: [`read_number()`·`read_text()`·`read_answer()`](quiz_game.py#L68), 진행: [`play_quiz()`·`finish_quiz()`](quiz_game.py#L145), 저장: [`storage.py`](storage.py) | “한 함수가 한 가지 역할만 하도록 나눴습니다. 입력 규칙 변경은 입력 함수, 채점 변경은 게임 함수, JSON 변경은 `storage.py`만 먼저 보면 됩니다.” |
| `state.json` 읽기·쓰기는 언제 어떤 순서로 일어나는가? | 시작: [`__init__()`](quiz_game.py#L15), 읽기: [`load_state()`](storage.py#L66), 쓰기: [`save_state()`](storage.py#L109) | “객체 생성 때 파일을 읽어 Quiz 객체로 바꿉니다. 저장할 때는 Quiz를 dict로 바꾸고 임시 JSON을 완성한 뒤 `os.replace()`로 원본을 교체합니다.” |
| `Ctrl+C` 또는 EOF에서 어떻게 안전 종료하는가? | [`run()`의 except와 finally](quiz_game.py#L39) | “`KeyboardInterrupt`와 `EOFError`를 잡아 안내하고, `finally`에서 정상·중단 여부와 관계없이 마지막 상태 저장을 시도합니다.” [`test_eof_exits_safely`](tests/test_game.py#L84)가 확인합니다. |
| 커밋 단위와 메시지 규칙은 무엇인가? | [Git 작업 방법](#10-git-작업-방법), [최근 Git 증빙](docs/git-evidence.txt) | “기능, 수정, 테스트, 문서를 서로 다른 커밋으로 나눴고 `Type(scope): 변경 요약` 형태를 사용했습니다. 예시는 `Refactor(beginner)`, `Fix(storage)`, `Test(bonus)`, `Docs(beginner)`입니다.” |

### 11.3 항목 3 — 핵심 기술 원리

| 평가 질문 | 바로 답할 내용 | 코드 근거 |
| --- | --- | --- |
| 클래스를 사용한 이유와 함수만 쓸 때의 차이는? | “문제의 데이터와 그 데이터에 필요한 동작을 한 객체에 묶기 위해 사용했습니다. 함수만 쓰면 `question`, `choices`, `answer`, `hint`를 여러 함수에 계속 전달해야 합니다. 클래스는 `self`로 현재 객체의 상태를 함께 관리합니다.” | [`Quiz.__init__()`](quiz.py#L6), [`QuizGame.__init__()`](quiz_game.py#L15) |
| JSON으로 저장하는 이유와 특징은? | “JSON은 사람이 직접 읽기 쉽고 `list`, `dict`, `str`, `int`와 잘 맞으며 외부 라이브러리가 필요 없습니다. 이 프로젝트처럼 작은 데이터를 저장하기에 간단합니다.” | [`Quiz.to_dict()`·`from_dict()`](quiz.py#L55), [`json.load()`·`json.dump()`](storage.py#L66) |
| 파일 입출력에 `try/except`가 필요한 이유는? | “파일 없음, 권한 문제, 손상된 JSON, 필드 누락, 잘못된 자료형이 생길 수 있기 때문입니다. 읽기 실패는 백업 후 기본값 복구, 쓰기 실패는 안내 후 `False` 반환으로 처리합니다.” | [`load_state()` 예외 처리](storage.py#L66), [`save_state()` 예외 처리](storage.py#L109) |
| 브랜치를 나눈 이유와 merge의 의미는? | “안정적인 `main`을 건드리지 않고 새 구조를 독립적으로 개발·테스트하기 위해 브랜치를 사용했습니다. merge는 검증이 끝난 브랜치 이력을 `main`에 합치는 것입니다.” | 브랜치 `codex/simple-quiz-rebuild`, 병합 `8016b24` |
| 현재 `state.json` 구조로 설계한 이유는? | “`quizzes`는 여러 문제이므로 list, 각 문제는 이름이 있는 값들이므로 dict입니다. `best_score`는 대표 결과 한 개, `score_history`는 시간순 결과 여러 개라서 각각 dict와 list로 나눴습니다.” | [`state.json` 설명](#8-statejson-설명), [`save_state()`의 data dict](storage.py#L116) |

### 11.4 항목 4 — 심층 인터뷰

#### 질문 1. 퀴즈가 1,000개 이상이면 JSON 방식에 어떤 한계가 생기나요?

**답변:** “현재는 시작할 때 전체 JSON을 메모리에 읽고, 수정할 때 전체 파일을
다시 씁니다. 데이터가 커지면 시작·저장 시간이 늘고, 검색할 때 모든 문제를
확인해야 하며, 여러 실행이 동시에 저장할 때 충돌할 수 있습니다. 먼저 검색용
번호나 카테고리를 추가하고 페이지 단위로 보여 주며, 더 커지면 필요한 행만
처리할 수 있는 SQLite로 바꾸겠습니다.” 자세한 내용은 [12장](#12-데이터가-많아질-때)에
정리했습니다.

#### 질문 2. `state.json`이 손상되면 데이터를 잃지 않도록 어떻게 대응하나요?

**답변:** “`json.load()`나 필드 검증이 실패하면 원본을 `state.json.bak`으로
복사하고 기본 퀴즈 18개로 새 파일을 만듭니다. 저장할 때도 원본에 바로 쓰지
않고 `.tmp` 파일을 완성한 뒤 교체해 중간에 파일이 잘릴 위험을 줄였습니다.”
구현은 [`load_state()`](storage.py#L66)와 [`save_state()`](storage.py#L109), 검증은
[`test_broken_file_is_recovered_and_backed_up`](tests/test_storage.py#L44)에 있습니다.

#### 질문 3. 채점 방식이나 선택지 개수가 바뀌면 어디부터 수정하나요?

**답변:** “채점 방식은 [`finish_quiz()`](quiz_game.py#L176)과
[`is_new_best()`](quiz_game.py#L208)을 먼저 수정하고 `test_game.py`를 확인합니다.
선택지 개수는 [`Quiz.__init__()`](quiz.py#L6)의 개수 검증,
[`Quiz.show()`](quiz.py#L40)의 출력 반복, [`read_answer()`](quiz_game.py#L117)의
입력 범위, [`add_quiz()`](quiz_game.py#L224)의 입력 반복을 함께 수정한 뒤
`test_quiz.py`와 `test_game.py`를 실행합니다.”

### 11.5 항목 5 — 보너스 문제 구현

| 보너스 | 구현 위치 | 동작과 검증 |
| --- | --- | --- |
| 랜덤 출제 | [`choose_questions()`](quiz_game.py#L107) | 원본 순서를 지키기 위해 목록을 복사한 뒤 `random.shuffle()`로 섞습니다. [`test_hint_deducts_score_and_history_is_saved`](tests/test_game.py#L41)에서 호출을 확인합니다. |
| 문제 수 선택 | [`choose_questions()`](quiz_game.py#L107) | 1부터 전체 문제 수 사이를 입력받고 `questions[:count]`만 출제합니다. 같은 테스트에서 결과의 `total`이 1인지 확인합니다. |
| 힌트와 감점 | [`read_answer()`](quiz_game.py#L117), [`finish_quiz()`](quiz_game.py#L176) | 한 문제에서 `h`는 한 번만 인정하고 힌트당 10점을 뺍니다. 최종 점수는 0점 아래로 내려가지 않습니다. |
| 퀴즈 삭제 | [`delete_quiz()`](quiz_game.py#L268) | 번호로 삭제한 뒤 즉시 저장합니다. 저장 실패 시 `insert()`로 원래 위치에 돌려놓습니다. [`test_add_and_delete_quiz`](tests/test_game.py#L58)가 재실행 상태까지 확인합니다. |
| 점수 히스토리 | [`finish_quiz()`](quiz_game.py#L176), [`show_scores()`](quiz_game.py#L286) | 매 게임의 시간, 문제 수, 정답 수, 힌트 수, 점수를 `score_history`에 저장하고 목록으로 보여 줍니다. |

### 평가 직전 1분 확인

```bash
python3 -m unittest discover -v
python3 main.py
git rev-list --count HEAD
git log --oneline --graph --decorate --all
```

말로 설명할 때는 **결론 → 구현 위치 → 테스트 또는 Git 근거** 순서로 답하면
짧고 명확합니다.

## 12. 데이터가 많아질 때

현재 방식은 모든 JSON을 한 번에 읽고 씁니다. 퀴즈가 1,000개 이상이면 다음
문제가 생길 수 있습니다.

- 시작할 때 전체 파일을 읽어 메모리 사용 증가
- 문제 하나만 바꿔도 전체 파일 다시 저장
- 제목 검색 시 모든 문제를 처음부터 확인
- 여러 프로그램이 동시에 저장하면 충돌 가능

이때는 카테고리·문제 번호 인덱스를 만들고, 페이지 단위로 보여 주며, 더 커지면
JSON 대신 SQLite 같은 데이터베이스를 사용합니다.

## 13. 요구사항이 바뀔 때 수정할 곳

| 변경 내용 | 먼저 볼 곳 | 함께 확인할 테스트 |
| --- | --- | --- |
| 정답 판정 | `quiz.py`의 `is_correct()` | `test_quiz.py` |
| 문제 수·랜덤 출제 | `choose_questions()` | `test_game.py` |
| 힌트 감점 | `read_answer()`, `finish_quiz()` | `test_game.py` |
| JSON 구조 | `storage.py`, `to_dict()` | `test_storage.py` |
| 메뉴 추가 | `show_menu()`, `run()` | `test_game.py` |

## 14. 제출 증빙

| 증빙 | 파일 |
| --- | --- |
| 개발 환경 | [`01-development-environment.png`](docs/screenshots/01-development-environment.png) |
| 퀴즈 추가 | [`02-add-quiz.png`](docs/screenshots/02-add-quiz.png) |
| 퀴즈 목록 | [`03-quiz-list.png`](docs/screenshots/03-quiz-list.png) |
| 퀴즈 플레이 | [`04-play-and-score.png`](docs/screenshots/04-play-and-score.png) |
| 브랜치 병합 | [`05-git-log-graph.png`](docs/screenshots/05-git-log-graph.png) |

평가 전 확인 명령은 다음과 같습니다.

```bash
python3 -m unittest discover -v
python3 main.py
git rev-list --count HEAD
git log --oneline --graph --decorate --all
```
