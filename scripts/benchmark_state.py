#!/usr/bin/env python3
"""QuizGame JSON 상태 저장·로드 비용을 재현 가능하게 측정한다."""

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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from quiz import Quiz  # noqa: E402
from quiz_game import QuizGame  # noqa: E402


def percentile(values: List[float], ratio: float) -> float:
    """작은 표본에서도 재현 가능한 nearest-rank 백분위수를 구한다."""
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * ratio) - 1)
    return ordered[index]


def build_quizzes(count: int) -> List[Quiz]:
    """측정용으로 동일한 크기의 유효한 퀴즈를 생성한다."""
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
    """저장·로드 중앙값·p95와 로드 피크 메모리를 측정한다."""
    with tempfile.TemporaryDirectory() as temporary_directory:
        state_file = Path(temporary_directory) / "state.json"
        game = QuizGame(output_func=lambda _: None, state_file=state_file)
        game.quizzes = build_quizzes(count)
        game.best_score = None

        save_times = []
        for _ in range(repeats):
            started = time.perf_counter()
            if not game.save_state():
                raise RuntimeError("벤치마크 상태를 저장하지 못했습니다.")
            save_times.append((time.perf_counter() - started) * 1_000)

        load_times = []
        peak_memory = []
        for _ in range(repeats):
            gc.collect()
            tracemalloc.start()
            started = time.perf_counter()
            restored = QuizGame(output_func=lambda _: None, state_file=state_file)
            load_times.append((time.perf_counter() - started) * 1_000)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            if len(restored.quizzes) != count:
                raise RuntimeError("로드한 퀴즈 개수가 원본과 다릅니다.")
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
