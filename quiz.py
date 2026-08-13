"""퀴즈 한 문제의 데이터와 동작을 정의하는 모델.

``QuizGame``이 게임 전체를 담당한다면 ``Quiz``는 문제 한 개만 담당한다.
이처럼 책임을 나누면 문제 형식이나 정답 판정 규칙을 바꿀 때 이 파일을
중심으로 수정할 수 있다.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Quiz:
    """문제, 네 개의 선택지, 정답 번호와 힌트를 표현한다.

    ``@dataclass``는 아래 네 속성을 받는 ``__init__``과 비교·출력에 필요한
    기본 메서드를 자동으로 만든다. 반복 코드를 줄이면서도 어떤 데이터를
    가진 객체인지 한눈에 보여 주는 Python 기능이다.

    ``answer``는 사용자가 보는 번호와 같도록 1부터 4까지 사용한다.
    반면 Python 리스트의 위치(index)는 0부터 시작하므로 선택지를 꺼낼 때는
    ``answer - 1``로 변환해야 한다.
    """

    question: str
    choices: List[str]
    answer: int
    hint: str = "힌트가 없습니다."

    def __post_init__(self) -> None:
        """객체 생성 직후 입력값을 정리하고 잘못된 퀴즈를 거부한다.

        dataclass가 만든 ``__init__`` 다음에 자동 호출된다. 파일에서 읽은 값과
        사용자가 입력한 값이 모두 이 검증을 거치므로, 나머지 코드는 항상
        '선택지 4개와 유효한 정답 번호가 있다'고 믿고 단순하게 작성할 수 있다.
        """
        # 먼저 자료형을 검사해야 아래의 strip(), 반복 처리를 안전하게 쓸 수 있다.
        if not isinstance(self.question, str):
            raise ValueError("문제는 문자열이어야 합니다.")
        if not isinstance(self.choices, list) or any(
            not isinstance(choice, str) for choice in self.choices
        ):
            raise ValueError("선택지는 문자열 목록이어야 합니다.")
        if not isinstance(self.hint, str):
            raise ValueError("힌트는 문자열이어야 합니다.")
        # 앞뒤 공백을 제거해 "   " 같은 입력도 빈 값으로 정확히 판단한다.
        self.question = self.question.strip()
        self.choices = [choice.strip() for choice in self.choices]
        self.hint = self.hint.strip()

        # 자료형이 맞더라도 내용과 개수가 규칙에 맞는지 한 번 더 검사한다.
        if not self.question:
            raise ValueError("문제는 비어 있을 수 없습니다.")
        if len(self.choices) != 4:
            raise ValueError("선택지는 정확히 4개여야 합니다.")
        if any(not choice for choice in self.choices):
            raise ValueError("선택지는 비어 있을 수 없습니다.")
        if len(set(self.choices)) != 4:
            raise ValueError("선택지는 서로 달라야 합니다.")
        # bool은 int의 하위 자료형이라 isinstance(True, int)가 True이다.
        # 따라서 True/False가 정답 번호로 통과하지 않도록 먼저 따로 제외한다.
        if isinstance(self.answer, bool) or not isinstance(self.answer, int):
            raise ValueError("정답 번호는 정수여야 합니다.")
        if not 1 <= self.answer <= 4:
            raise ValueError("정답 번호는 1부터 4 사이여야 합니다.")
        if not self.hint:
            raise ValueError("힌트는 비어 있을 수 없습니다.")

    def format_question(self, number: int) -> str:
        """문제 번호, 질문, 선택지를 한 덩어리의 문자열로 만든다.

        화면 출력 자체는 ``QuizGame``이 담당하고, 이 메서드는 출력할 문자열만
        반환한다. 반환값을 사용하면 터미널 없이도 결과 문자열을 테스트할 수 있다.
        """
        lines = ["-" * 40, f"[문제 {number}]", self.question, ""]
        # enumerate(..., start=1)는 리스트 항목에 1부터 번호를 붙여 준다.
        lines.extend(
            f"{index}. {choice}"
            for index, choice in enumerate(self.choices, start=1)
        )
        return "\n".join(lines)

    def is_correct(self, selected: int) -> bool:
        """사용자가 고른 번호와 정답 번호를 비교해 bool로 반환한다."""
        return selected == self.answer

    def to_dict(self) -> Dict[str, Any]:
        """Quiz 객체를 JSON이 저장할 수 있는 dict로 변환한다.

        JSON은 사용자 정의 객체를 바로 저장할 수 없으므로 str, int, list,
        dict처럼 JSON이 이해하는 기본 자료형으로 바꾸는 과정이 필요하다.
        ``choices``는 복사본을 만들어 반환하여 외부 변경이 원본에 번지지 않게 한다.
        """
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        """JSON에서 읽은 dict를 검증된 Quiz 객체로 되돌린다.

        ``classmethod``의 ``cls``는 Quiz 클래스 자체를 가리킨다. 마지막의
        ``cls(...)``가 객체를 만들면 ``__post_init__`` 검증도 자동으로 실행된다.
        예전 저장 파일에 hint가 없으면 기본 문구를 사용해 호환성을 유지한다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        return cls(
            question=data.get("question", ""),
            choices=data.get("choices", []),
            answer=data.get("answer", 0),
            hint=data.get("hint", "힌트가 없습니다."),
        )
