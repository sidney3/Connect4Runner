from datetime import timedelta
from typing import Optional
import time


class Timer:
    def __init__(self):
        self._last_start_ns: Optional[int] = None

    def start(self):
        self._last_start_ns = time.perf_counter_ns()

    def stop(self) -> timedelta:
        end_ns = time.perf_counter_ns()
        assert self._last_start_ns

        return timedelta(microseconds=(end_ns - self._last_start_ns) / 1_000)
