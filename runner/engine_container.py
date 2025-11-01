import os
import asyncio
import subprocess
from typing import TypeVar, List, Optional, Coroutine, Any, Union
import runner.codec as codec
from datetime import timedelta
import time


class Timeout:
    pass


class EngineContainer:
    def __init__(self, timeout: timedelta, args: List[str]):
        self._loop = asyncio.new_event_loop()
        self._timeout = timeout

        self._engine = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,
            start_new_session=True,
        )

    def read_message(self):
        reader = self._engine.stdout
        assert reader

        before = time.perf_counter_ns()

        msg = codec.decode_buffer(reader)

        after = time.perf_counter_ns()

        time_taken = timedelta(microseconds=(after - before) / 1_000)

        if time_taken > self._timeout:
            print(f"took too long. {time_taken}. Time allowed: {self._timeout}")
            return Timeout()

        return msg

    def send_move(self, to_move: codec.Move):
        writer = self._engine.stdin
        assert writer

        writer.write(codec.MoveMsg.make(to_move).encode())

    def send_game_params(self, to_make: codec.Params):
        writer = self._engine.stdin
        assert writer

        msg = codec.ParamsMsg.make(to_make).encode()
        writer.write(msg)
