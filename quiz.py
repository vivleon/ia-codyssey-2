"""개별 퀴즈 모델."""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Quiz:
    """문제, 네 개의 선택지, 정답 번호를 표현한다."""

    question: str
    choices: List[str]
    answer: int

    def __post_init__(self) -> None:
        self.question = self.question.strip()
        self.choices = [str(choice).strip() for choice in self.choices]

        if not self.question:
            raise ValueError("문제는 비어 있을 수 없습니다.")
        if len(self.choices) != 4:
            raise ValueError("선택지는 정확히 4개여야 합니다.")
        if any(not choice for choice in self.choices):
            raise ValueError("선택지는 비어 있을 수 없습니다.")
        if len(set(self.choices)) != 4:
            raise ValueError("선택지는 서로 달라야 합니다.")
        if isinstance(self.answer, bool) or not isinstance(self.answer, int):
            raise ValueError("정답 번호는 정수여야 합니다.")
        if not 1 <= self.answer <= 4:
            raise ValueError("정답 번호는 1부터 4 사이여야 합니다.")

    def format_question(self, number: int) -> str:
        """터미널에 표시할 문제 문자열을 만든다."""
        lines = ["-" * 40, f"[문제 {number}]", self.question, ""]
        lines.extend(
            f"{index}. {choice}"
            for index, choice in enumerate(self.choices, start=1)
        )
        return "\n".join(lines)

    def is_correct(self, selected: int) -> bool:
        """선택한 번호가 정답인지 확인한다."""
        return selected == self.answer

    def to_dict(self) -> Dict[str, Any]:
        """JSON으로 저장할 수 있는 사전으로 변환한다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        """JSON에서 읽은 사전으로 Quiz를 만든다."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        return cls(
            question=data.get("question", ""),
            choices=data.get("choices", []),
            answer=data.get("answer", 0),
        )

