"""퀴즈 한 문제를 담당하는 파일"""


class Quiz:
    # __init__은 Quiz 객체를 만들 때 처음 한 번 실행된다.
    def __init__(self, question, choices, answer, hint="힌트가 없습니다."):
        # 잘못된 퀴즈가 만들어지지 않도록 먼저 확인한다.
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있을 수 없습니다.")

        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")

        clean_choices = []

        # for와 if를 사용해 선택지를 하나씩 확인한다.
        for choice in choices:
            if not isinstance(choice, str) or not choice.strip():
                raise ValueError("선택지는 비어 있을 수 없습니다.")

            clean_choice = choice.strip()

            if clean_choice in clean_choices:
                raise ValueError("선택지는 서로 달라야 합니다.")

            clean_choices.append(clean_choice)

        if type(answer) is not int or answer < 1 or answer > 4:
            raise ValueError("정답은 1부터 4 사이의 숫자여야 합니다.")

        if not isinstance(hint, str) or not hint.strip():
            raise ValueError("힌트는 비어 있을 수 없습니다.")

        # self는 지금 만들어진 Quiz 객체 자신을 뜻한다.
        self.question = question.strip()
        self.choices = clean_choices
        self.answer = answer
        self.hint = hint.strip()

    def show(self, number):
        """문제와 선택지를 화면에 보여 준다."""
        print("-" * 40)
        print("[문제", number, "]")
        print(self.question)
        print()

        # 선택지 4개를 차례대로 출력한다.
        for index in range(4):
            print(str(index + 1) + ".", self.choices[index])

    def is_correct(self, selected):
        """사용자가 고른 번호가 정답인지 알려 준다."""
        return selected == self.answer

    def to_dict(self):
        """Quiz 객체를 JSON에 저장할 수 있는 dict로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """JSON에서 읽은 dict를 Quiz 객체로 바꾼다."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터가 올바르지 않습니다.")

        # cls(...)는 새로운 Quiz 객체를 만든다.
        return cls(
            data.get("question", ""),
            data.get("choices", []),
            data.get("answer", 0),
            data.get("hint", "힌트가 없습니다."),
        )
