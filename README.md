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

## 11. 데이터가 많아질 때

현재 방식은 모든 JSON을 한 번에 읽고 씁니다. 퀴즈가 1,000개 이상이면 다음
문제가 생길 수 있습니다.

- 시작할 때 전체 파일을 읽어 메모리 사용 증가
- 문제 하나만 바꿔도 전체 파일 다시 저장
- 제목 검색 시 모든 문제를 처음부터 확인
- 여러 프로그램이 동시에 저장하면 충돌 가능

이때는 카테고리·문제 번호 인덱스를 만들고, 페이지 단위로 보여 주며, 더 커지면
JSON 대신 SQLite 같은 데이터베이스를 사용합니다.

## 12. 요구사항이 바뀔 때 수정할 곳

| 변경 내용 | 먼저 볼 곳 | 함께 확인할 테스트 |
| --- | --- | --- |
| 정답 판정 | `quiz.py`의 `is_correct()` | `test_quiz.py` |
| 문제 수·랜덤 출제 | `choose_questions()` | `test_game.py` |
| 힌트 감점 | `read_answer()`, `finish_quiz()` | `test_game.py` |
| JSON 구조 | `storage.py`, `to_dict()` | `test_storage.py` |
| 메뉴 추가 | `show_menu()`, `run()` | `test_game.py` |

## 13. 제출 증빙

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
