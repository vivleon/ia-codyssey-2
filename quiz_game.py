"""메뉴와 퀴즈 게임 전체를 담당하는 파일"""

import os
import random
from datetime import datetime

from quiz import Quiz
from storage import load_state, save_state


class QuizGame:
    # 힌트 한 번을 사용하면 10점을 뺀다.
    HINT_PENALTY = 10

    def __init__(self, state_file=None):
        """게임에 필요한 데이터를 준비한다."""
        if state_file is None:
            project_folder = os.path.dirname(os.path.abspath(__file__))
            state_file = os.path.join(project_folder, "state.json")

        self.state_file = state_file
        self.quizzes, self.best_score, self.score_history = load_state(state_file)
        self.running = True

    def show_menu(self):
        """사용자가 선택할 수 있는 메뉴를 보여 준다."""
        print()
        print("=" * 40)
        print("       AI와 Python 기초 퀴즈")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 종료")
        print("=" * 40)

    def run(self):
        """종료를 선택할 때까지 메뉴를 반복한다."""
        try:
            while self.running:
                self.show_menu()
                menu = self.read_number("선택: ", 1, 6)

                # 메뉴 번호에 따라 서로 다른 기능을 실행한다.
                if menu == 1:
                    self.play_quiz()
                elif menu == 2:
                    self.add_quiz()
                elif menu == 3:
                    self.list_quizzes()
                elif menu == 4:
                    self.show_scores()
                elif menu == 5:
                    self.delete_quiz()
                else:
                    self.running = False
                    print("게임을 종료합니다.")

        except (KeyboardInterrupt, EOFError):
            print("\n입력이 중단되어 안전하게 종료합니다.")

        finally:
            # 정상 종료와 Ctrl+C 종료 모두 마지막 상태를 저장한다.
            self.save()

    def read_number(self, message, minimum, maximum):
        """범위 안의 숫자를 입력할 때까지 다시 묻는다."""
        while True:
            text = input(message).strip()

            if text == "":
                print("값을 입력해 주세요.")
                continue

            try:
                number = int(text)
            except ValueError:
                print("숫자로 입력해 주세요.")
                continue

            if minimum <= number <= maximum:
                return number

            print(minimum, "부터", maximum, "사이의 숫자를 입력해 주세요.")

    def read_text(self, message):
        """빈 글자가 아닌 내용을 입력할 때까지 다시 묻는다."""
        while True:
            text = input(message).strip()

            if text != "":
                return text

            print("내용을 입력해 주세요.")

    def save(self):
        """현재 상태를 state.json에 저장한다."""
        return save_state(
            self.state_file,
            self.quizzes,
            self.best_score,
            self.score_history,
        )

    def choose_questions(self):
        """문제를 섞고 사용자가 고른 개수만 돌려준다."""
        questions = self.quizzes.copy()
        random.shuffle(questions)

        message = "몇 문제를 풀까요? (1-" + str(len(questions)) + "): "
        count = self.read_number(message, 1, len(questions))

        return questions[:count]

    def read_answer(self, quiz):
        """정답 번호를 받고 힌트 사용 여부도 함께 돌려준다."""
        hint_used = False

        while True:
            text = input("정답 입력 (1-4, 힌트 h): ").strip().lower()

            if text == "h":
                if hint_used:
                    print("이 문제의 힌트는 이미 사용했습니다.")
                else:
                    hint_used = True
                    print("힌트:", quiz.hint)
                    print("최종 점수에서 10점이 차감됩니다.")

                continue

            try:
                answer = int(text)
            except ValueError:
                print("1부터 4 사이의 숫자 또는 h를 입력해 주세요.")
                continue

            if 1 <= answer <= 4:
                return answer, hint_used

            print("1부터 4 사이의 숫자 또는 h를 입력해 주세요.")

    def play_quiz(self):
        """퀴즈를 출제하고 점수를 계산한다."""
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        questions = self.choose_questions()
        correct_count = 0
        hint_count = 0

        print()
        print("퀴즈를 시작합니다! 총", len(questions), "문제입니다.")

        # 고른 문제를 하나씩 차례대로 푼다.
        for number in range(len(questions)):
            quiz = questions[number]
            quiz.show(number + 1)

            answer, hint_used = self.read_answer(quiz)

            if quiz.is_correct(answer):
                correct_count = correct_count + 1
                print("정답입니다!")
            else:
                print("오답입니다. 정답은", quiz.answer, "번입니다.")

            if hint_used:
                hint_count = hint_count + 1

        self.finish_quiz(correct_count, len(questions), hint_count)

    def finish_quiz(self, correct_count, total, hint_count):
        """최종 점수를 계산하고 기록을 저장한다."""
        score = round(correct_count / total * 100)
        score = score - hint_count * self.HINT_PENALTY

        # 힌트를 많이 사용해도 점수는 0점보다 작아지지 않는다.
        if score < 0:
            score = 0

        print()
        print("결과:", total, "문제 중", correct_count, "문제 정답")
        print("최종 점수:", score, "점")

        result = {
            "correct": correct_count,
            "total": total,
            "percentage": score,
            "hints_used": hint_count,
        }

        if self.is_new_best(result):
            self.best_score = result.copy()
            print("새로운 최고 점수입니다!")

        # 모든 게임 기록에 날짜와 시간을 함께 저장한다.
        history = result.copy()
        now = datetime.now().astimezone()
        history["played_at"] = now.isoformat(timespec="seconds")
        self.score_history.append(history)

        self.save()

    def is_new_best(self, result):
        """새 결과가 지금까지의 최고 점수보다 좋은지 확인한다."""
        if self.best_score is None:
            return True

        old_score = self.best_score["percentage"]
        new_score = result["percentage"]

        if new_score > old_score:
            return True

        if new_score == old_score:
            return result["correct"] > self.best_score["correct"]

        return False

    def add_quiz(self):
        """새 퀴즈를 입력받아 목록과 파일에 저장한다."""
        print()
        print("새로운 퀴즈를 추가합니다.")

        question = self.read_text("문제: ")
        choices = []

        # 선택지 4개를 입력받는다.
        for number in range(1, 5):
            while True:
                choice = self.read_text("선택지 " + str(number) + ": ")

                if choice in choices:
                    print("이미 입력한 선택지입니다.")
                else:
                    choices.append(choice)
                    break

        answer = self.read_number("정답 번호 (1-4): ", 1, 4)
        hint = self.read_text("힌트: ")

        new_quiz = Quiz(question, choices, answer, hint)
        self.quizzes.append(new_quiz)

        if self.save():
            print("퀴즈가 추가되었습니다!")
        else:
            # 저장할 수 없으면 목록도 추가하기 전으로 되돌린다.
            self.quizzes.pop()
            print("저장에 실패하여 퀴즈 추가를 취소했습니다.")

    def list_quizzes(self):
        """등록된 퀴즈 목록을 보여 준다."""
        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        print()
        print("등록된 퀴즈 목록 - 총", len(self.quizzes), "개")

        for number in range(len(self.quizzes)):
            print(str(number + 1) + ".", self.quizzes[number].question)

    def delete_quiz(self):
        """선택한 퀴즈를 삭제하고 파일에도 저장한다."""
        if len(self.quizzes) == 0:
            print("삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()
        number = self.read_number("삭제할 퀴즈 번호: ", 1, len(self.quizzes))

        deleted_quiz = self.quizzes.pop(number - 1)

        if self.save():
            print("'" + deleted_quiz.question + "' 퀴즈를 삭제했습니다.")
        else:
            # 저장에 실패하면 메모리의 목록도 삭제 전으로 되돌린다.
            self.quizzes.insert(number - 1, deleted_quiz)
            print("저장에 실패하여 삭제를 취소했습니다.")

    def show_scores(self):
        """최고 점수와 지금까지의 모든 게임 기록을 보여 준다."""
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다.")
            return

        print()
        print("최고 점수:", self.best_score["percentage"], "점")
        print("전체 게임 기록:", len(self.score_history), "회")

        for number in range(len(self.score_history)):
            record = self.score_history[number]
            print(
                str(number + 1) + ".",
                record["played_at"],
                "|",
                record["total"],
                "문제 |",
                record["correct"],
                "정답 |",
                record["percentage"],
                "점",
            )
