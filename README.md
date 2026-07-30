# 🤖 AI 탐험 퀴즈 게임

Python 기본 문법, 객체 지향, JSON 파일 입출력, Git 워크플로우를 한 번에
연습하기 위해 만든 터미널 퀴즈 게임입니다. 프로그램을 종료한 뒤 다시
실행해도 사용자가 추가한 퀴즈와 최고 점수가 `state.json`에 유지됩니다.

## 퀴즈 주제와 선정 이유

주제는 **AI와 Python 기초**입니다. AI를 사용할 때 필요한 기본 개념과
검증 태도를 익히는 동시에, 이 프로그램을 구성하는 Python 문법도 함께
복습할 수 있어 선정했습니다. 직접 작성한 기본 퀴즈 6개가 포함되어
있습니다.

## 실행 환경

- Python 3.10 이상
- 외부 라이브러리 없음(표준 라이브러리만 사용)
- 개발 및 테스트 확인 환경: Python 3.13.12

## 실행 방법

```bash
git clone https://github.com/vivleon/ia-codyssey-2.git
cd ia-codyssey-2
python3 --version
python3 main.py
```

메뉴에서 `1`부터 `5`까지 원하는 기능의 번호를 입력합니다.

```text
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
```

자동 테스트는 다음 명령으로 실행합니다.

```bash
python3 -m unittest discover -v
```

## 기능 목록

- 기본 AI·Python 퀴즈 6개 제공
- 저장된 모든 문제를 무작위 순서로 출제
- 정답/오답 안내와 100점 기준 결과 계산
- 새로운 최고 점수 자동 비교 및 저장
- 문제, 서로 다른 선택지 4개, 정답 번호를 입력해 퀴즈 추가
- 저장된 퀴즈 목록과 정답 확인
- 빈 입력, 숫자가 아닌 입력, 범위 밖 숫자 재입력 처리
- `Ctrl+C`와 입력 스트림 종료(EOF) 시 현재 상태 저장 후 안전 종료
- 상태 파일이 없으면 기본 데이터 사용
- JSON이 손상되었거나 스키마가 잘못되면 기본 데이터로 자동 복구
- 한글을 보존하는 UTF-8 JSON 저장

## 파일 구조

```text
.
├── main.py                    # 프로그램 시작점
├── quiz.py                    # Quiz 클래스와 데이터 변환
├── quiz_game.py               # QuizGame 클래스와 전체 게임 흐름
├── defaults.py                # 기본 퀴즈 6개
├── state.json                 # 퀴즈와 최고 점수 영속 데이터
├── tests/
│   ├── test_quiz.py           # Quiz 모델 테스트
│   ├── test_menu.py           # 메뉴와 공통 입력 테스트
│   ├── test_play.py           # 출제와 채점 테스트
│   └── test_game_features.py  # 저장, 복구, 등록, 조회 통합 테스트
├── .gitignore
└── README.md
```

## 클래스 구조

### `Quiz`

- 속성: `question`, `choices`, `answer`
- 선택지가 정확히 4개인지, 중복이나 빈 값이 없는지 검증
- 문제 출력 문자열 생성, 정답 확인, JSON용 사전 변환 담당

### `QuizGame`

- 속성: 퀴즈 목록, 최고 점수, 상태 파일 경로
- 메뉴, 입력 검증, 출제, 등록, 목록, 점수, 저장/불러오기 담당
- 파일 오류와 사용자 입력 중단을 처리하고 가능한 범위에서 안전하게 저장

## 데이터 파일 설명

`state.json`은 항상 프로젝트 루트에 있으며 UTF-8로 읽고 씁니다.
프로그램은 임시 파일에 먼저 기록한 뒤 교체하는 방식으로 저장 중 파일이
일부만 작성될 위험을 줄입니다.

```json
{
  "quizzes": [
    {
      "question": "문제 내용",
      "choices": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
      "answer": 2
    }
  ],
  "best_score": {
    "correct": 4,
    "total": 6,
    "percentage": 67
  }
}
```

- `quizzes`: 퀴즈 객체 목록
- `question`: 문제 문자열
- `choices`: 선택지 4개의 문자열 목록
- `answer`: 1부터 4 사이의 정답 번호
- `best_score`: 정답 수, 전체 문제 수, 100점 기준 점수
- 아직 플레이하지 않았다면 `best_score`는 `null`

## 사용한 Python 개념

- `str`, `int`, `bool`, `list`, `dict`로 입력과 상태 표현
- `if/elif/else`로 메뉴와 정답 조건 분기
- `while`로 메뉴 및 재입력 반복, `for`로 문제와 선택지 순회
- 함수의 매개변수와 반환값으로 입력, 출력, 저장 책임 분리
- `Quiz`, `QuizGame` 클래스로 개별 데이터와 전체 흐름 분리
- `try/except/finally`로 변환 오류, 파일 오류, 안전 종료 처리
- `json` 모듈로 Python 객체와 JSON 데이터 변환

## Git 실습 기록

- `codex/quiz-play` 브랜치에서 출제·채점 기능과 테스트를 구현
- `main`에 `--no-ff` 방식으로 병합해 브랜치 작업 기록 보존
- 메뉴, 모델, 데이터, 출제, 저장, 등록, 조회, 테스트, 문서를 기능별 커밋
- 개발 완료 후 별도 디렉터리에서 clone → 수정 → commit → push를 수행하고,
  기존 작업 디렉터리에서 pull로 반영

주요 명령의 역할:

| 명령 | 역할 |
| --- | --- |
| `git init` | 현재 폴더에 새 로컬 저장소 생성 |
| `git add` | 다음 커밋에 포함할 변경 선택 |
| `git commit` | 선택한 변경을 하나의 이력으로 기록 |
| `git push` | 로컬 커밋을 원격 저장소에 전송 |
| `git pull` | 원격 변경을 가져와 현재 브랜치에 통합 |
| `git checkout` | 브랜치를 만들거나 전환 |
| `git clone` | 원격 저장소 전체를 새 로컬 폴더에 복제 |

## Git 이력 확인

```bash
git log --oneline --graph --decorate --all
```

이 명령으로 기능별 커밋, `codex/quiz-play` 브랜치, 병합 커밋을 확인할 수
있습니다.
