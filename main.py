"""퀴즈 게임을 시작하는 파일"""

from quiz_game import QuizGame


def main():
    # QuizGame 객체를 만들고 게임을 시작한다.
    game = QuizGame()
    game.run()


# 이 파일을 직접 실행했을 때만 main()을 실행한다.
if __name__ == "__main__":
    main()
