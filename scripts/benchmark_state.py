#!/usr/bin/env python3
"""QuizGame JSON 상태 저장·로드 시간과 메모리를 측정하는 보조 도구.

실제 게임 기능에는 사용되지 않는다. README의 '퀴즈가 많아질 때 JSON 방식에
어떤 한계가 생기는가?'라는 설명을 추측이 아닌 측정값으로 확인하기 위한 코드다.
"""

import argparse
import gc
import math
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List

# 이 스크립트는 scripts 폴더 안에 있으므로 부모의 부모가 프로젝트 루트다.
# 루트를 import 검색 경로에 넣어 어디에서 실행해도 quiz 모듈을 찾게 한다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from quiz import Quiz  # noqa: E402
from quiz_game import QuizGame  # noqa: E402


def percentile(values: List[float], ratio: float) -> float:
    """정렬된 값에서 nearest-rank 방식의 백분위수를 구한다.

    p95는 측정값의 약 95%가 이 값 이하라는 의미다. 평균만 볼 때 가려질 수 있는
    느린 실행을 함께 보여 준다.
    """
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * ratio) - 1)
    return ordered[index]


def build_quizzes(count: int) -> List[Quiz]:
    """요청한 개수만큼 서로 구분되는 유효한 측정용 Quiz를 만든다.

    리스트 컴프리헨션은 반복문으로 append하는 과정을 간결하게 표현한 문법이다.
    ``index % 4 + 1``은 정답 번호가 1~4 사이에서 반복되게 한다.
    """
    return [
        Quiz(
            f"벤치마크 문제 {index:05d}",
            [
                f"선택지 A-{index:05d}",
                f"선택지 B-{index:05d}",
                f"선택지 C-{index:05d}",
                f"선택지 D-{index:05d}",
            ],
            index % 4 + 1,
        )
        for index in range(count)
    ]


def measure(count: int, repeats: int) -> Dict[str, float]:
    """한 데이터 크기의 저장·로드 시간과 로드 피크 메모리를 측정한다.

    임시 폴더는 측정이 끝나면 자동 삭제되어 실제 state.json을 건드리지 않는다.
    ``perf_counter``는 짧은 실행 시간을 측정하는 고해상도 시계이고,
    ``tracemalloc``은 Python이 로드 중 사용한 메모리의 최고점을 기록한다.
    여러 번 측정한 뒤 중앙값과 p95를 사용해 일시적인 흔들림의 영향을 줄인다.
    """
    with tempfile.TemporaryDirectory() as temporary_directory:
        state_file = Path(temporary_directory) / "state.json"
        game = QuizGame(output_func=lambda _: None, state_file=state_file)
        game.quizzes = build_quizzes(count)
        game.best_score = None

        # 밀리초(ms)로 바꾸기 위해 초 단위 차이에 1,000을 곱한다.
        save_times = []
        for _ in range(repeats):
            started = time.perf_counter()
            if not game.save_state():
                raise RuntimeError("벤치마크 상태를 저장하지 못했습니다.")
            save_times.append((time.perf_counter() - started) * 1_000)

        load_times = []
        peak_memory = []
        for _ in range(repeats):
            # 이전 반복에서 남은 객체를 정리해 메모리 측정 조건을 비슷하게 맞춘다.
            gc.collect()
            tracemalloc.start()
            started = time.perf_counter()
            restored = QuizGame(output_func=lambda _: None, state_file=state_file)
            load_times.append((time.perf_counter() - started) * 1_000)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if len(restored.quizzes) != count:
                raise RuntimeError("로드한 퀴즈 개수가 원본과 다릅니다.")
            # byte를 MiB 단위로 바꾼다: 1 MiB = 1024 * 1024 byte.
            peak_memory.append(peak / 1024 / 1024)

        return {
            "count": float(count),
            "size_kib": state_file.stat().st_size / 1024,
            "save_ms": statistics.median(save_times),
            "save_p95_ms": percentile(save_times, 0.95),
            "load_ms": statistics.median(load_times),
            "load_p95_ms": percentile(load_times, 0.95),
            "peak_mib": statistics.median(peak_memory),
        }


def main() -> None:
    """명령행 옵션을 읽고 각 크기의 측정 결과를 Markdown 표로 출력한다."""
    # argparse는 --sizes, --repeats 같은 명령행 옵션과 도움말을 처리한다.
    parser = argparse.ArgumentParser(
        description="QuizGame JSON 저장·로드 벤치마크"
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[10, 100, 1_000, 5_000],
        help="측정할 퀴즈 개수(기본: 10 100 1000 5000)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="각 측정의 반복 횟수(기본: 5)",
    )
    arguments = parser.parse_args()
    if arguments.repeats < 1 or any(size < 1 for size in arguments.sizes):
        parser.error("퀴즈 개수와 반복 횟수는 1 이상이어야 합니다.")

    print(f"Python {platform.python_version()} / {platform.platform()}")
    print(
        f"반복 {arguments.repeats}회: 중앙값과 nearest-rank p95"
    )
    print(
        "| 퀴즈 수 | JSON (KiB) | 저장 중앙 (ms) | 저장 p95 (ms) | "
        "로드 중앙 (ms) | 로드 p95 (ms) | 로드 피크 (MiB) |"
    )
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    # 출력 형식을 Markdown 표로 맞춰 README에 결과를 쉽게 옮길 수 있다.
    for size in arguments.sizes:
        result = measure(size, arguments.repeats)
        print(
            f"| {int(result['count']):,} | {result['size_kib']:.1f} | "
            f"{result['save_ms']:.2f} | {result['save_p95_ms']:.2f} | "
            f"{result['load_ms']:.2f} | {result['load_p95_ms']:.2f} | "
            f"{result['peak_mib']:.2f} |"
        )


if __name__ == "__main__":
    main()
